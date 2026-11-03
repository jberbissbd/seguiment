"""Generació del PDF d'una distribució de taules d'aula.

El document reprodueix el mateix llenguatge visual que la pantalla
(colors, amplada reduïda dels passadissos, taula del professor
destacada, alumnes en format "Cognoms, Nom", professor a baix) perquè el
que es veu a l'aplicació i el que s'exporta siguin el mateix pla, no dues
representacions diferents.
"""

from pathlib import Path
from xml.sax.saxutils import escape

from tutopy.models.classroom_layout import CellType, ClassroomLayout, LayoutGrid
from tutopy.models.messaging import Student
from tutopy.services.exceptions import ValidationError
from tutopy.services.utils import sanitize_xml_text

AISLE_WEIGHT = 0.5
SEAT_BACKGROUND_HEX = "#EAF2FB"
SEAT_BORDER_HEX = "#2B73B7"
SEAT_TEXT_HEX = "#2C3E50"
TEACHER_BACKGROUND_HEX = "#2B73B7"


class ClassroomLayoutReportService:
    """Genera el PDF d'una distribució d'aula ja carregada (graella i alumnes)."""

    def export_pdf(
        self, layout: ClassroomLayout, grid: LayoutGrid,
        students_by_id: dict[int, Student], destination: str | Path,
    ) -> Path:
        """Desa `grid` (amb els alumnes de `students_by_id`) com a PDF.

        Args:
            layout: Metadades de la distribució (nom, grup, taula del
                professor, data de l'última modificació).
            grid: Graella a representar (model, no el widget).
            students_by_id: Alumnes assignats a la graella, indexats per
                identificador.
            destination: Ruta de destinació (l'extensió es normalitza a
                `.pdf`).

        Returns:
            Ruta final del fitxer generat.

        Raises:
            ValidationError: Si no s'ha pogut desar el document.
        """
        path = self._destination(destination)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            self._save_pdf(path, layout, grid, students_by_id)
        except (OSError, ValueError) as error:
            raise ValidationError("No s’ha pogut desar el pla de distribució.") from error
        return path

    @staticmethod
    def _destination(destination: str | Path) -> Path:
        path = Path(destination)
        if not path.name:
            raise ValidationError("Cal indicar una destinació per al document.")
        if path.suffix.lower() != ".pdf":
            path = path.with_suffix(".pdf")
        return path

    def _save_pdf(
        self, path: Path, layout: ClassroomLayout, grid: LayoutGrid,
        students_by_id: dict[int, Student],
    ) -> None:
        from datetime import date

        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="TutopyTitle", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=6,
        ))
        story = [
            Paragraph(escape(self._safe(layout.name)), styles["TutopyTitle"]),
            Paragraph(
                f"<b>Grup:</b> {escape(self._safe(layout.group_name))}", styles["BodyText"],
            ),
            Paragraph(
                "<b>Última modificació:</b> "
                f"{date.fromisoformat(layout.updated_at).strftime('%d/%m/%Y')}",
                styles["BodyText"],
            ),
            Spacer(1, 0.4 * cm),
            self._build_grid_table(grid, students_by_id),
        ]
        if layout.teacher_mode == "strip":
            story.append(Spacer(1, 0.3 * cm))
            story.append(self._build_teacher_strip(layout.teacher_position))

        pagesize = landscape(A4) if grid.columns >= grid.rows else A4
        pdf = SimpleDocTemplate(
            str(path), pagesize=pagesize, rightMargin=1.5 * cm, leftMargin=1.5 * cm,
            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
            title=self._safe(layout.name), subject="Distribució d'aula",
        )
        pdf.build(story)

    def _build_grid_table(self, grid: LayoutGrid, students_by_id: dict[int, Student]):
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import Table, TableStyle

        seat_column_width = 2.4 * cm
        column_weights = self._column_weights(grid)
        column_widths = [seat_column_width * weight for weight in column_weights]
        seat_style = ParagraphStyle(
            name="SeatCell", fontName="Helvetica-Bold", fontSize=7.5, leading=9,
            alignment=TA_CENTER, textColor=colors.HexColor(SEAT_TEXT_HEX),
        )
        teacher_style = ParagraphStyle(
            name="TeacherCell", parent=seat_style, textColor=colors.white,
        )

        data = []
        style_commands = [
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]
        # Fila 0 és el davant (a prop del professor): es dibuixa a baix de
        # la pàgina, igual que a la pantalla, així que es recorren les
        # files del model de la darrera a la primera.
        for display_row, row in enumerate(reversed(range(grid.rows))):
            row_cells = []
            for column in range(grid.columns):
                cell = grid.cells[(row, column)]
                content, box = self._cell_presentation(
                    cell, students_by_id, seat_style, teacher_style,
                )
                row_cells.append(content)
                if box is not None:
                    background, border = box
                    style_commands.append(
                        ("BACKGROUND", (column, display_row), (column, display_row), background)
                    )
                    style_commands.append(
                        ("BOX", (column, display_row), (column, display_row), 0.75, border)
                    )
            data.append(row_cells)

        table = Table(data, colWidths=column_widths, rowHeights=1.5 * cm)
        table.setStyle(TableStyle(style_commands))
        return table

    def _cell_presentation(self, cell, students_by_id, seat_style, teacher_style):
        """Retorna `(contingut, (fons, vora) | None)` d'una cel·la per a la taula PDF."""
        from reportlab.lib import colors
        from reportlab.platypus import Paragraph

        if cell.cell_type == CellType.TEACHER:
            return (
                Paragraph("Professor", teacher_style),
                (colors.HexColor(TEACHER_BACKGROUND_HEX), colors.HexColor(TEACHER_BACKGROUND_HEX)),
            )
        if cell.cell_type == CellType.SEAT and cell.student_id is not None:
            student = students_by_id.get(cell.student_id)
            name = escape(self._safe(student.filing_name)) if student else ""
            return (
                Paragraph(name, seat_style),
                (colors.HexColor(SEAT_BACKGROUND_HEX), colors.HexColor(SEAT_BORDER_HEX)),
            )
        return "", None

    @staticmethod
    def _column_weights(grid: LayoutGrid) -> list[float]:
        """Amplada relativa de cada columna, igual que a la graella en pantalla."""
        return [
            AISLE_WEIGHT if grid.cells[(0, column)].cell_type == CellType.AISLE else 1.0
            for column in range(grid.columns)
        ]

    @staticmethod
    def _build_teacher_strip(teacher_position: str):
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, Table, TableStyle

        style = ParagraphStyle(
            name="TeacherStrip", fontName="Helvetica-Bold", fontSize=9,
            alignment=TA_CENTER, textColor=colors.white,
        )
        table = Table(
            [[Paragraph("Taula del professor", style)]], colWidths=[4.5 * cm], rowHeights=[1 * cm],
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(TEACHER_BACKGROUND_HEX)),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(TEACHER_BACKGROUND_HEX)),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        table.hAlign = {"left": "LEFT", "right": "RIGHT"}.get(teacher_position, "CENTER")
        return table

    @staticmethod
    def _safe(value) -> str:
        return sanitize_xml_text(value)
