from dataclasses import dataclass
from pathlib import Path

from tutopy.services.exceptions import ValidationError
from tutopy.services.open_document_report_service import OpenDocumentReportService
from tutopy.services.spreadsheet_report_service import SpreadsheetReportService
from tutopy.services.word_report_service import WordReportService


@dataclass(frozen=True, slots=True)
class ReportFormat:
    label: str
    extension: str


class ReportFileService:
    """Selecciona el generador adequat i exporta un informe a un fitxer."""

    FORMATS = {
        "xlsx": ReportFormat("Full de càlcul Excel", "xlsx"),
        "docx": ReportFormat("Document de text Word", "docx"),
        "odt": ReportFormat("Document de text OpenDocument", "odt"),
        "pdf": ReportFormat("Document PDF", "pdf"),
    }

    def __init__(
        self,
        spreadsheets: SpreadsheetReportService,
        word_reports: WordReportService,
        open_document_reports: OpenDocumentReportService,
    ):
        self.spreadsheets = spreadsheets
        self.word_reports = word_reports
        self.open_document_reports = open_document_reports

    def get_format(self, report_format: str) -> ReportFormat:
        try:
            return self.FORMATS[report_format]
        except (KeyError, TypeError) as error:
            raise ValidationError("El format de l’informe no és vàlid.") from error

    def export_student(
        self,
        student_id: int,
        destination: str | Path,
        report_format: str,
        include_terms: bool = False,
    ) -> Path:
        """Exporta un informe individual en el format sol·licitat."""
        self.get_format(report_format)
        if report_format == "xlsx":
            return self.spreadsheets.export_student(
                student_id, destination, include_terms=include_terms
            )
        if report_format == "docx":
            return self.word_reports.export_student(student_id, destination)
        return self.open_document_reports.export_student(
            student_id, destination, report_format
        )
