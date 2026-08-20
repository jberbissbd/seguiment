"""Exportació i importació portable d'agregats complets d'alumnes."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from tutopy import __version__
from tutopy.models.messaging import (
    CategoryNew, ContactNew, NoteNew, StudentAnnotationNew, StudentGroupHistoryNew,
    StudentNew,
)
from tutopy.models.transfer import (
    TransferAction, TransferConflict, TransferDecision, TransferPreview,
    TransferResult,
)
from tutopy.services.exceptions import (
    EntityNotFoundError, TransferAuthenticationError, TransferFormatError,
    ValidationError,
)
from tutopy.services.validation_service import ValidationService


@dataclass(frozen=True, slots=True)
class TransferExportPreparation:
    """Snapshot d'una transferència que ja no requereix lectures SQLite."""

    student_ids: tuple[int, ...]
    destination: Path
    password: str
    students_by_id: dict
    categories: dict[int, str]
    courses: dict[int, str]
    related: dict


class TransferService:
    """Mou dades d'alumnes entre instàncies mitjançant paquets versionats."""

    FORMAT = "tutopy-transfer"
    FORMAT_VERSION = 1
    EXTENSION = ".tpy"
    MAX_ARCHIVE_SIZE = 1_000 * 1024 * 1024
    MAX_UNCOMPRESSED_SIZE = 2_000 * 1024 * 1024
    MAX_MEMBERS = 20_000
    ENVELOPE_MAGIC = b"TUTOPY\x00"
    ENVELOPE_VERSION = 1
    SALT_SIZE = 16
    NONCE_SIZE = 12
    TAG_SIZE = 16
    SCRYPT_N = 2**15
    SCRYPT_R = 8
    SCRYPT_P = 1
    KEY_SIZE = 32
    CHUNK_SIZE = 1024 * 1024

    def __init__(
        self, students, notes, categories, courses, contacts, annotations,
        documents, history, document_service, transaction_factory,
    ):
        self.students = students
        self.notes = notes
        self.categories = categories
        self.courses = courses
        self.contacts = contacts
        self.annotations = annotations
        self.documents = documents
        self.history = history
        self.document_service = document_service
        self.transaction_factory = transaction_factory
        self.validation = ValidationService()

    def export_student(
        self, student_id: int, destination: str | Path, password: str,
    ) -> Path:
        """Exporta un únic alumne i totes les seves dades relacionades."""
        student_id = self.validation.positive_id(student_id)
        return self.export_students([student_id], destination, password)

    def export_all(self, destination: str | Path, password: str) -> Path:
        """Exporta tots els alumnes de la instància en un sol paquet."""
        return self.export_students(
            [student.id for student in self.students.get_all()], destination, password
        )

    def export_students(
        self, student_ids: list[int], destination: str | Path, password: str,
    ) -> Path:
        """Construeix un paquet `.tpy` amb els alumnes indicats."""
        preparation = self.prepare_export(student_ids, destination, password)
        return self.export_prepared(preparation)

    def prepare_export(
        self, student_ids: list[int], destination: str | Path, password: str,
    ) -> TransferExportPreparation:
        """Valida i carrega totes les dades abans d'iniciar un treballador."""
        password = self._validate_password(password)
        if not student_ids:
            raise ValidationError("No hi ha alumnes per exportar.")
        if len(student_ids) != len(set(student_ids)):
            raise ValidationError("La selecció d’alumnes conté duplicats.")
        path = Path(destination)
        if path.suffix.lower() != self.EXTENSION:
            path = path.with_suffix(self.EXTENSION)
        if not path.name:
            raise ValidationError("Cal indicar un fitxer de destinació.")

        validated_ids = [self.validation.positive_id(item) for item in student_ids]
        students_by_id = self.students.get_by_ids(validated_ids)
        missing_ids = [item for item in validated_ids if item not in students_by_id]
        if missing_ids:
            raise EntityNotFoundError(
                f"L’alumne amb ID {missing_ids[0]} no existeix."
            )
        categories = {item.id: item.name for item in self.categories.get_all()}
        courses = {item.id: item.course for item in self.courses.get_all()}
        related = self._related_by_student(validated_ids)
        return TransferExportPreparation(
            tuple(validated_ids), path, password, students_by_id,
            categories, courses, related,
        )

    def export_prepared(
        self, preparation: TransferExportPreparation,
        progress_callback=None, cancel_requested=None,
    ) -> Path | None:
        """Comprimeix i xifra un snapshot sense consultar SQLite."""
        payload = []
        document_sources: list[tuple[Path, str]] = []
        checksums = {}
        total = len(preparation.student_ids)
        for completed, student_id in enumerate(preparation.student_ids, 1):
            if cancel_requested is not None and cancel_requested():
                return None
            student = preparation.students_by_id[student_id]
            item, sources = self._export_student_data(
                student, preparation.categories, preparation.courses,
                preparation.related,
            )
            payload.append(item)
            for source, archive_name in sources:
                digest = self._sha256_file(source)
                checksums[archive_name] = digest
                item["documents_by_path"][archive_name]["sha256"] = digest
                item["documents_by_path"][archive_name]["size"] = source.stat().st_size
                document_sources.append((source, archive_name))
            item["documents"] = list(item.pop("documents_by_path").values())
            if progress_callback is not None:
                progress_callback(completed, total)

        if cancel_requested is not None and cancel_requested():
            return None

        manifest = {
            "format": self.FORMAT,
            "format_version": self.FORMAT_VERSION,
            "application_version": __version__,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "scope": "single_student" if len(payload) == 1 else "multiple_students",
            "student_count": len(payload),
        }
        data = {"students": payload}
        try:
            preparation.destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="tutopy-export-") as temporary:
                plain_path = Path(temporary) / "payload.zip"
                with ZipFile(plain_path, "w", compression=ZIP_DEFLATED) as archive:
                    archive.writestr("manifest.json", self._json(manifest))
                    archive.writestr("data.json", self._json(data))
                    archive.writestr("checksums.json", self._json(checksums))
                    for source, archive_name in document_sources:
                        archive.write(source, archive_name)
                self._encrypt_file(
                    plain_path, preparation.destination, preparation.password
                )
        except OSError as error:
            reason = error.strerror or str(error)
            raise ValidationError(
                f"No s’ha pogut crear el paquet de transferència: {reason}."
            ) from error
        return preparation.destination

    def analyze(self, source: str | Path, password: str) -> TransferPreview:
        """Valida completament un paquet sense modificar dades locals."""
        path, data = self._read_package(source, password, verify_documents=True)
        conflicts = []
        note_count = document_count = total_bytes = 0
        for item in data["students"]:
            local = self.students.get_by_uuid(item["uuid"])
            if local:
                conflicts.append(TransferConflict(
                    item["uuid"], self._full_name(item), local.full_name,
                ))
            note_count += len(item["notes"])
            document_count += len(item["documents"])
            total_bytes += sum(document["size"] for document in item["documents"])
        return TransferPreview(
            path, len(data["students"]), note_count, document_count,
            total_bytes, tuple(conflicts),
        )

    def execute(
        self, preview: TransferPreview,
        decisions: tuple[TransferDecision, ...] = (),
        password: str = "",
    ) -> TransferResult:
        """Importa el paquet de manera transaccional segons les decisions donades."""
        path, data = self._read_package(
            preview.source, password, verify_documents=True
        )
        decision_by_uuid = {decision.uuid: decision.action for decision in decisions}
        conflict_uuids = {
            item["uuid"] for item in data["students"]
            if self.students.get_by_uuid(item["uuid"]) is not None
        }
        missing = conflict_uuids - decision_by_uuid.keys()
        unknown = decision_by_uuid.keys() - conflict_uuids
        if missing:
            raise ValidationError("Falten decisions per a alguns alumnes en conflicte.")
        if (
            unknown or len(decision_by_uuid) != len(decisions)
            or any(not isinstance(item.action, TransferAction) for item in decisions)
        ):
            raise ValidationError("Les decisions de transferència no són vàlides.")

        created = replaced = skipped = imported_as_new = imported_documents = 0
        new_file_paths: list[Path] = []
        old_file_paths: list[Path] = []
        with tempfile.TemporaryDirectory(prefix="tutopy-transfer-") as temporary:
            temporary_path = Path(temporary)
            self._extract_documents(path, password, data, temporary_path)
            try:
                with self.transaction_factory():
                    category_ids = self._category_ids(data)
                    course_ids = self._course_ids(data)
                    for item in data["students"]:
                        local = self.students.get_by_uuid(item["uuid"])
                        action = decision_by_uuid.get(item["uuid"])
                        if local and action == TransferAction.KEEP_LOCAL:
                            skipped += 1
                            continue
                        target_uuid = item["uuid"]
                        if local and action == TransferAction.REPLACE:
                            old_file_paths.extend(
                                Path(document.file_path)
                                for document in self.documents.get_by_student(local.id)
                                if document.file_path
                            )
                            self.students.delete(local.id)
                            replaced += 1
                        elif local and action == TransferAction.IMPORT_AS_NEW:
                            target_uuid = str(uuid.uuid4())
                            imported_as_new += 1
                        else:
                            created += 1
                        student = self.students.create_with_uuid(
                            StudentNew(
                                self.validation.person_name(
                                    item["name"], "El nom no és vàlid."
                                ),
                                self.validation.person_name(
                                    item["surnames"], "Els cognoms no són vàlids."
                                ),
                                self.validation.optional_text(item["group_name"]),
                            ),
                            target_uuid,
                        )
                        count = self._import_related(
                            student.id, item, category_ids, course_ids,
                            temporary_path, new_file_paths,
                        )
                        imported_documents += count
            except Exception:
                self._remove_managed_files(new_file_paths)
                raise
        self._remove_managed_files(old_file_paths)
        return TransferResult(
            created, replaced, skipped, imported_as_new, imported_documents
        )

    def _related_by_student(self, student_ids):
        return {
            "notes": self.notes.get_by_students(student_ids),
            "contacts": self.contacts.get_by_students(student_ids),
            "annotations": self.annotations.get_by_students(student_ids),
            "history": self.history.get_by_students(student_ids),
            "documents": self.documents.get_by_students(student_ids),
        }

    def _export_student_data(self, student, categories, courses, related):
        notes = [{
            "date": item.date, "content": item.content,
            "category": categories[item.category_id], "course": courses[item.course_id],
        } for item in related["notes"][student.id]]
        contacts = [{
            "name": item.name, "description": item.description,
            "phone": item.phone, "email": item.email,
        } for item in related["contacts"][student.id]]
        annotations = [
            {"content": item.content}
            for item in related["annotations"][student.id]
        ]
        history = [{
            "group_name": item.group_name,
            "course": courses.get(item.academic_course_id),
            "start_date": item.start_date, "end_date": item.end_date,
        } for item in related["history"][student.id]]
        documents_by_path = {}
        sources = []
        for item in related["documents"][student.id]:
            source = self.document_service.get_readable_document_path(item)
            archive_name = f"documents/{student.uuid}/{item.uuid_filename}"
            documents_by_path[archive_name] = {
                "name": item.name, "description": item.description,
                "original_filename": item.original_filename, "date": item.date,
                "course": courses.get(item.course_id), "archive_path": archive_name,
            }
            sources.append((source, archive_name))
        return ({
            "uuid": student.uuid, "name": student.name,
            "surnames": student.surnames, "group_name": student.group_name,
            "notes": notes, "contacts": contacts, "annotations": annotations,
            "history": history, "documents_by_path": documents_by_path,
        }, sources)

    def _import_related(
        self, student_id, item, category_ids, course_ids, temporary,
        created_file_paths,
    ):
        for note in item["notes"]:
            self.notes.create(NoteNew(
                student_id, category_ids[self._category_key(note["category"])],
                note["date"], course_ids[note["course"]], note["content"],
            ))
        for contact in item["contacts"]:
            self.contacts.create(ContactNew(student_id=student_id, **contact))
        for annotation in item["annotations"]:
            self.annotations.create(StudentAnnotationNew(
                student_id, annotation["content"]
            ))
        for history in item["history"]:
            self.history.create(StudentGroupHistoryNew(
                student_id=student_id, group_name=history["group_name"],
                academic_course_id=(course_ids[history["course"]]
                                    if history["course"] else None),
                start_date=history["start_date"], end_date=history["end_date"],
            ))
        count = 0
        for document in item["documents"]:
            created = self.document_service.import_file(
                student_id, document["name"], document["description"],
                str(temporary / document["archive_path"]), document["date"],
            )
            created_file_paths.append(Path(created.file_path))
            count += 1
        return count

    def _category_ids(self, data):
        by_key = {
            self._category_key(item.name): item.id
            for item in self.categories.get_all()
        }
        names = {
            note["category"] for student in data["students"]
            for note in student["notes"]
        }
        for name in sorted(names, key=str.casefold):
            key = self._category_key(name)
            if key not in by_key:
                by_key[key] = self.categories.create(CategoryNew(name)).id
        return by_key

    def _course_ids(self, data):
        names = set()
        for student in data["students"]:
            names.update(note["course"] for note in student["notes"])
            names.update(item["course"] for item in student["history"] if item["course"])
            names.update(item["course"] for item in student["documents"] if item["course"])
        return {name: self.courses.get_or_create(name).id for name in names}

    def _read_package(self, source, password, verify_documents):
        path = Path(source)
        if not path.is_file() or path.suffix.lower() != self.EXTENSION:
            raise ValidationError("Cal seleccionar un paquet .tpy vàlid.")
        if path.stat().st_size > self.MAX_ARCHIVE_SIZE:
            raise ValidationError("El paquet supera la mida màxima admesa.")
        try:
            with self._decrypted_archive(path, password) as archive:
                members = archive.infolist()
                if len(members) > self.MAX_MEMBERS:
                    raise ValidationError("El paquet conté massa fitxers.")
                if sum(item.file_size for item in members) > self.MAX_UNCOMPRESSED_SIZE:
                    raise ValidationError("El paquet descomprimit és massa gran.")
                if len({item.filename for item in members}) != len(members):
                    raise ValidationError("El paquet conté fitxers duplicats.")
                for member in members:
                    self._validate_member_name(member.filename)
                    if member.flag_bits & 0x1:
                        raise ValidationError("No s’admeten paquets ZIP xifrats.")
                manifest = self._load_json(archive, "manifest.json")
                data = self._load_json(archive, "data.json")
                checksums = self._load_json(archive, "checksums.json")
                self._validate_payload(manifest, data, checksums)
                if verify_documents:
                    for name, expected in checksums.items():
                        if self._sha256_bytes(archive.read(name)) != expected:
                            raise ValidationError("Un document del paquet està corrupte.")
        except (BadZipFile, KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise TransferFormatError(
                "El contingut del paquet de transferència està corrupte."
            ) from error
        return path, data

    def _validate_payload(self, manifest, data, checksums):
        if not all(isinstance(value, dict) for value in (manifest, data, checksums)):
            raise ValidationError("L’estructura JSON del paquet no és vàlida.")
        if manifest.get("format") != self.FORMAT:
            raise ValidationError("El fitxer no és un paquet de Tutopy.")
        if manifest.get("format_version") != self.FORMAT_VERSION:
            raise ValidationError("La versió del paquet no és compatible.")
        students = data.get("students")
        if not isinstance(students, list) or not students:
            raise ValidationError("El paquet no conté alumnes.")
        if manifest.get("student_count") != len(students):
            raise ValidationError("El manifest del paquet és inconsistent.")
        seen = set()
        for student in students:
            required = {
                "uuid", "name", "surnames", "group_name", "notes", "contacts",
                "annotations", "history", "documents",
            }
            if not isinstance(student, dict) or not required <= student.keys():
                raise ValidationError("Les dades d’un alumne són incompletes.")
            try:
                uuid.UUID(student["uuid"])
            except (ValueError, TypeError, AttributeError) as error:
                raise ValidationError("Un UUID d’alumne no és vàlid.") from error
            if student["uuid"] in seen:
                raise ValidationError("El paquet conté UUID d’alumne duplicats.")
            seen.add(student["uuid"])
            self.validation.person_name(student["name"], "El nom no és vàlid.")
            self.validation.person_name(student["surnames"], "Els cognoms no són vàlids.")
            self.validation.optional_text(student["group_name"])
            for key in ("notes", "contacts", "annotations", "history", "documents"):
                if not isinstance(student[key], list):
                    raise ValidationError("El contingut del paquet no és vàlid.")
            for note in student["notes"]:
                self._require_keys(note, "date", "content", "category", "course")
                self.validation.iso_date(note["date"])
                self.validation.required_text(note["content"], "Una nota no és vàlida.")
                self.validation.required_text(note["category"], "Una categoria no és vàlida.")
                self.validation.academic_course(note["course"])
            for contact in student["contacts"]:
                self._require_keys(contact, "name", "description", "phone", "email")
                self.validation.required_text(contact["name"], "Un contacte no és vàlid.")
                for key in ("description", "phone", "email"):
                    self.validation.optional_text(contact[key])
            for annotation in student["annotations"]:
                self._require_keys(annotation, "content")
                self.validation.required_text(
                    annotation["content"], "Un descriptor no és vàlid."
                )
            for item in student["history"]:
                self._require_keys(
                    item, "group_name", "course", "start_date", "end_date"
                )
                self.validation.required_text(
                    item["group_name"], "Un grup de l’historial no és vàlid."
                )
                self.validation.iso_date(item["start_date"])
                if item["end_date"] is not None:
                    self.validation.iso_date(item["end_date"])
                if item["course"] is not None:
                    self.validation.academic_course(item["course"])
            for document in student["documents"]:
                self._require_keys(
                    document, "name", "description", "original_filename", "date",
                    "course", "archive_path", "sha256", "size",
                )
                self.validation.required_text(
                    document["name"], "Un document no és vàlid."
                )
                self.validation.iso_date(document["date"])
                if document["course"] is not None:
                    self.validation.academic_course(document["course"])
                name = document.get("archive_path")
                if name not in checksums or document.get("sha256") != checksums[name]:
                    raise ValidationError("Els hashes dels documents són inconsistents.")
                if not isinstance(document.get("size"), int) or document["size"] < 0:
                    raise ValidationError("La mida d’un document no és vàlida.")

    @staticmethod
    def _require_keys(value, *keys):
        if not isinstance(value, dict) or not set(keys) <= value.keys():
            raise ValidationError("El contingut del paquet no és vàlid.")

    def _extract_documents(self, path, password, data, destination):
        with self._decrypted_archive(path, password) as archive:
            for student in data["students"]:
                for document in student["documents"]:
                    name = document["archive_path"]
                    target = destination / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(name) as source, target.open("wb") as output:
                        while chunk := source.read(1024 * 1024):
                            output.write(chunk)

    @classmethod
    def _validate_password(cls, password):
        if not isinstance(password, str) or len(password) < 8:
            raise ValidationError(
                "La contrasenya ha de tenir com a mínim 8 caràcters."
            )
        return password

    @classmethod
    def _derive_key(cls, password, salt):
        return Scrypt(
            salt=salt, length=cls.KEY_SIZE, n=cls.SCRYPT_N,
            r=cls.SCRYPT_R, p=cls.SCRYPT_P,
        ).derive(password.encode("utf-8"))

    @classmethod
    def _encrypt_file(cls, source, destination, password):
        salt = os.urandom(cls.SALT_SIZE)
        nonce = os.urandom(cls.NONCE_SIZE)
        header = (
            cls.ENVELOPE_MAGIC + bytes([cls.ENVELOPE_VERSION]) + salt + nonce
        )
        encryptor = Cipher(
            algorithms.AES(cls._derive_key(password, salt)), modes.GCM(nonce)
        ).encryptor()
        encryptor.authenticate_additional_data(header)
        temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
        try:
            with source.open("rb") as plain, temporary.open("xb") as encrypted:
                encrypted.write(header)
                while chunk := plain.read(cls.CHUNK_SIZE):
                    encrypted.write(encryptor.update(chunk))
                encrypted.write(encryptor.finalize())
                encrypted.write(encryptor.tag)
                encrypted.flush()
                os.fsync(encrypted.fileno())
            os.replace(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)

    @classmethod
    @contextmanager
    def _decrypted_archive(cls, source, password):
        cls._validate_password(password)
        header_size = len(cls.ENVELOPE_MAGIC) + 1 + cls.SALT_SIZE + cls.NONCE_SIZE
        if source.stat().st_size < header_size + cls.TAG_SIZE:
            raise TransferFormatError("El fitxer .tpy està incomplet.")
        with source.open("rb") as encrypted:
            header = encrypted.read(header_size)
            if not header.startswith(cls.ENVELOPE_MAGIC):
                raise TransferFormatError(
                    "El fitxer no és un paquet .tpy xifrat compatible."
                )
            version_offset = len(cls.ENVELOPE_MAGIC)
            if header[version_offset] != cls.ENVELOPE_VERSION:
                raise TransferFormatError(
                    "La versió de xifrat del paquet no és compatible."
                )
            salt_start = version_offset + 1
            salt = header[salt_start:salt_start + cls.SALT_SIZE]
            nonce = header[-cls.NONCE_SIZE:]
            encrypted.seek(-cls.TAG_SIZE, os.SEEK_END)
            tag = encrypted.read(cls.TAG_SIZE)
            ciphertext_size = source.stat().st_size - header_size - cls.TAG_SIZE
            encrypted.seek(header_size)
            decryptor = Cipher(
                algorithms.AES(cls._derive_key(password, salt)),
                modes.GCM(nonce, tag),
            ).decryptor()
            decryptor.authenticate_additional_data(header)
            try:
                with tempfile.TemporaryFile() as plain:
                    remaining = ciphertext_size
                    while remaining:
                        chunk = encrypted.read(min(cls.CHUNK_SIZE, remaining))
                        if not chunk:
                            raise TransferFormatError("El fitxer .tpy està incomplet.")
                        plain.write(decryptor.update(chunk))
                        remaining -= len(chunk)
                    plain.write(decryptor.finalize())
                    plain.seek(0)
                    with ZipFile(plain) as archive:
                        yield archive
            except InvalidTag as error:
                raise TransferAuthenticationError(
                    "La contrasenya és incorrecta o el paquet ha estat manipulat."
                ) from error

    def _remove_managed_files(self, paths):
        if self.document_service.storage_dir is None:
            return
        storage = self.document_service.storage_dir.resolve()
        for path in paths:
            try:
                resolved = path.resolve()
                if resolved.parent == storage:
                    resolved.unlink(missing_ok=True)
            except OSError:
                pass

    @staticmethod
    def _validate_member_name(name):
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            raise ValidationError("El paquet conté una ruta no segura.")
        allowed = name in {"manifest.json", "data.json", "checksums.json"}
        if not allowed and not name.startswith("documents/"):
            raise ValidationError("El paquet conté fitxers desconeguts.")

    @staticmethod
    def _load_json(archive, name):
        return json.loads(archive.read(name).decode("utf-8"))

    @staticmethod
    def _json(value):
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )

    @staticmethod
    def _sha256_file(path):
        digest = hashlib.sha256()
        with path.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _sha256_bytes(value):
        return hashlib.sha256(value).hexdigest()

    @staticmethod
    def _category_key(value):
        return " ".join(value.casefold().split())

    @staticmethod
    def _full_name(student):
        return f"{student['name']} {student['surnames']}".strip()
