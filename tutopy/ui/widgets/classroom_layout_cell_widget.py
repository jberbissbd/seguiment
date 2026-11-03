"""Cel·la individual del pla de distribució d'aula."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDrag, QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QMenu, QVBoxLayout, QWidget

from tutopy.models.classroom_layout import CellType
from tutopy.models.messaging import Student
from tutopy.ui.styles import PRIMARY_COLOR, TEXT_PRIMARY
from tutopy.ui.widgets import classroom_layout_mime as mime
from tutopy.ui.widgets.avatar import circular_pixmap

CELL_WIDTH = 92
CELL_HEIGHT = 80
# Un passadís no necessita l'amplada d'una taula: mig seient ja el
# representa prou bé i aprofita millor l'espai de la graella.
AISLE_WIDTH = CELL_WIDTH // 2
PHOTO_SIZE = 36
CELL_MARGIN = 4
LAYOUT_SPACING = 2
NAME_FONT_SIZE = 10
NAME_FONT_MIN_SIZE = 7
NAME_CONTENT_WIDTH = CELL_WIDTH - 2 * CELL_MARGIN
NAME_CONTENT_HEIGHT = CELL_HEIGHT - 2 * CELL_MARGIN
NAME_CONTENT_HEIGHT_WITH_PHOTO = NAME_CONTENT_HEIGHT - LAYOUT_SPACING - PHOTO_SIZE

# Un sol color per a tots els alumnes: amb grups grans, una paleta de
# poques opcions acaba repetint color entre alumnes diferents (confon més
# del que ajuda); el nom ja identifica qui seu a cada seient.
SEAT_BACKGROUND = "#EAF2FB"
SEAT_BORDER = PRIMARY_COLOR
SEAT_TEXT = TEXT_PRIMARY
TEACHER_BACKGROUND = PRIMARY_COLOR
TEACHER_TEXT = "#FFFFFF"

CELL_TYPE_LABELS = {
    CellType.EMPTY: "",
    CellType.AISLE: "···",
    CellType.TEACHER: "Professor",
}


def _name_font(pixel_size: int = NAME_FONT_SIZE) -> QFont:
    """Font amb què es mesura i es dibuixa el nom, igual per a tothom.

    Es construeix explícitament (en lloc de llegir-la del `QLabel` en
    viu) perquè els càlculs de mida siguin fiables fins i tot abans que
    l'estil CSS s'hagi aplicat del tot al widget.
    """
    font = QFont()
    font.setPixelSize(pixel_size)
    font.setWeight(QFont.Weight.DemiBold)
    return font


def _fitting_font_size(text: str, max_width: int, max_height: int) -> int:
    """Retorna la mida de lletra més gran (fins a `NAME_FONT_SIZE`) amb què `text` hi cap.

    `text` es mostra sencer, amb ajust de línia per amplada; si amb
    `NAME_FONT_SIZE` no hi càpiguen totes les línies necessàries en
    `max_height`, es va reduint la mida (mai per sota de
    `NAME_FONT_MIN_SIZE`) en lloc d'escurçar el text.
    """
    for size in range(NAME_FONT_SIZE, NAME_FONT_MIN_SIZE - 1, -1):
        metrics = QFontMetrics(_name_font(size))
        bounds = metrics.boundingRect(
            0, 0, max_width, 10_000, int(Qt.TextFlag.TextWordWrap), text,
        )
        if bounds.height() <= max_height:
            return size
    return NAME_FONT_MIN_SIZE


class ClassroomCellWidget(QFrame):
    """Una cel·la de la graella: seient (buit o amb alumne), passadís, buit o professor.

    Els seients ocupats mostren el nom i els cognoms de l'alumne (i la seva
    foto, si `show_photos` ho demana) — mai només les inicials, perquè
    qualsevol que consulti la distribució (no només qui l'ha creada) pugui
    identificar l'alumne sense haver de passar-hi el cursor per sobre.

    No conté cap lògica de negoci: només emet senyals quan l'usuari hi
    interactua; el controlador decideix com interpretar-les.
    """

    move_requested = Signal(int, str, int, int)
    """student_id, origen, fila de destí, columna de destí."""
    type_change_requested = Signal(int, int, str)
    """fila, columna, nou `CellType.value`."""
    teacher_place_requested = Signal(int, int)
    """fila, columna on col·locar la taula del professor."""
    return_to_pending_requested = Signal(int)
    """student_id a tornar a la llista de pendents."""

    def __init__(self, row: int, column: int, parent: QWidget | None = None):
        """Construeix una cel·la buida a la posició de model `(row, column)`."""
        super().__init__(parent)
        self.row = row
        self.column = column
        self.setObjectName("classroomCell")
        self.setFixedHeight(CELL_HEIGHT)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_label.setFixedHeight(PHOTO_SIZE)
        layout.addWidget(self.photo_label)
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label, 1)

        self._cell_type = CellType.SEAT
        self._student: Student | None = None
        self.update_cell(CellType.SEAT, None, None, False)

    def update_cell(
        self, cell_type: CellType, student: Student | None, photo_path: str | None,
        show_photos: bool,
    ) -> None:
        """Actualitza l'aparença d'aquesta cel·la.

        Args:
            cell_type: Tipus de la cel·la.
            student: Alumne assignat, o `None` si la cel·la és buida.
            photo_path: Ruta de la foto de l'alumne, si en té.
            show_photos: Si cal mostrar també la foto, a sobre del nom.
        """
        self._cell_type = cell_type
        self._student = student
        self.setFixedWidth(AISLE_WIDTH if cell_type == CellType.AISLE else CELL_WIDTH)
        self.setProperty("cellType", cell_type.value)
        self.photo_label.setPixmap(QPixmap())
        self.photo_label.setVisible(False)
        self.name_label.setStyleSheet("")
        self.name_label.setText("")
        self.setStyleSheet("")
        self.setToolTip("")
        if cell_type == CellType.SEAT and student is not None:
            pixmap = circular_pixmap(photo_path, PHOTO_SIZE) if show_photos and photo_path else None
            if pixmap is not None:
                self.photo_label.setPixmap(pixmap)
                self.photo_label.setVisible(True)
            self.setStyleSheet(
                f"QFrame#classroomCell {{ background-color: {SEAT_BACKGROUND}; "
                f"border: 1px solid {SEAT_BORDER}; border-radius: 6px; }}"
            )
            available_height = (
                NAME_CONTENT_HEIGHT_WITH_PHOTO if pixmap is not None else NAME_CONTENT_HEIGHT
            )
            font_size = _fitting_font_size(
                student.filing_name, NAME_CONTENT_WIDTH, available_height,
            )
            self.name_label.setStyleSheet(
                f"color: {SEAT_TEXT}; font-size: {font_size}px; font-weight: 600; "
                "background: transparent; border: none;"
            )
            self.name_label.setText(student.filing_name)
            self.setToolTip(student.filing_name)
        elif cell_type == CellType.TEACHER:
            self.setStyleSheet(
                f"QFrame#classroomCell {{ background-color: {TEACHER_BACKGROUND}; "
                f"border: 2px solid {TEACHER_BACKGROUND}; border-radius: 6px; }}"
            )
            self.name_label.setStyleSheet(
                f"color: {TEACHER_TEXT}; font-size: 10px; font-weight: 700; "
                "background: transparent; border: none;"
            )
            self.name_label.setText(CELL_TYPE_LABELS[CellType.TEACHER])
        else:
            self.name_label.setText(CELL_TYPE_LABELS.get(cell_type, ""))
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event) -> None:
        """Inicia un arrossegament si la cel·la té un alumne assignat."""
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._cell_type == CellType.SEAT and self._student is not None
        ):
            drag = QDrag(self)
            drag.setMimeData(mime.encode(
                self._student.id, mime.cell_origin(self.row, self.column),
            ))
            drag.exec(Qt.DropAction.MoveAction)
            return
        super().mousePressEvent(event)

    def dragEnterEvent(self, event) -> None:
        """Accepta l'arrossegament d'un alumne si la cel·la és un seient."""
        if self._cell_type == CellType.SEAT and mime.decode(event.mimeData()) is not None:
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        """Emet `move_requested` amb l'alumne i l'origen arrossegats."""
        if self._handle_drop(event.mimeData()):
            event.acceptProposedAction()

    def _handle_drop(self, mime_data) -> bool:
        """Decodifica `mime_data` i emet `move_requested` si la cel·la és un seient.

        Separat de `dropEvent` perquè es pugui testejar sense passar per
        `QDropEvent.acceptProposedAction()`, que requereix una sessió real
        d'arrossegament de Qt i no es pot invocar de manera fiable sobre un
        esdeveniment construït a mà (hi ha un problema conegut de PySide6
        que hi provoca una violació de segment fora d'una sessió real).

        Returns:
            Si la cel·la ha acceptat el `drop` (per decidir si cridar
            `acceptProposedAction`).
        """
        if self._cell_type != CellType.SEAT:
            return False
        decoded = mime.decode(mime_data)
        if decoded is None:
            return False
        student_id, origin = decoded
        self.move_requested.emit(student_id, origin, self.row, self.column)
        return True

    def _show_menu(self, position) -> None:
        menu = QMenu(self)
        for cell_type, label in (
            (CellType.SEAT, "Seient"), (CellType.EMPTY, "Buit"),
            (CellType.AISLE, "Passadís"),
        ):
            menu.addAction(label, lambda value=cell_type.value: self.type_change_requested.emit(
                self.row, self.column, value,
            ))
        menu.addSeparator()
        menu.addAction(
            "Col·locar la taula del professor aquí",
            lambda: self.teacher_place_requested.emit(self.row, self.column),
        )
        if self._student is not None:
            menu.addSeparator()
            menu.addAction(
                "Tornar a pendents",
                lambda student_id=self._student.id: self.return_to_pending_requested.emit(
                    student_id,
                ),
            )
        menu.exec(self.mapToGlobal(position))
