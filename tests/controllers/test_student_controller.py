"""
Tests per al StudentController.
"""
import pytest
from unittest.mock import MagicMock, patch
from tutopy.controllers.student_controller import StudentController
from tutopy.models.messaging import Student, StudentNew


@pytest.fixture
def mock_student_service():
    """Fixture que crea un servei d'alumnes mock."""
    service = MagicMock()
    service.get_all.return_value = []
    service.get_student_by_id.return_value = None
    service.search.return_value = []
    service.create_student.return_value = Student(
        id=1, uuid="test-uuid", name="Test", surnames="User", group_name="4t A"
    )
    return service


@pytest.fixture
def mock_category_service():
    """Fixture que crea un servei de categories mock."""
    service = MagicMock()
    service.get_all.return_value = []
    return service


@pytest.fixture
def mock_academic_course_service():
    """Fixture que crea un servei de cursos acadèmics mock."""
    service = MagicMock()
    service.get_all.return_value = []
    return service


@pytest.fixture
def student_controller(mock_student_service, mock_category_service, mock_academic_course_service):
    """Fixture que crea un StudentController."""
    return StudentController(
        mock_student_service,
        mock_category_service,
        mock_academic_course_service
    )


class TestStudentControllerInitialization:
    """Tests per a la inicialització del StudentController."""
    
    def test_controller_creation(self, student_controller):
        """Verifica que el controlador es crea correctament."""
        assert student_controller is not None
        assert isinstance(student_controller, StudentController)
    
    def test_controller_has_services(self, student_controller, mock_student_service, 
                                    mock_category_service, mock_academic_course_service):
        """Verifica que el controlador té els serveis injectats."""
        assert student_controller.student_service == mock_student_service
        assert student_controller.category_service == mock_category_service
        assert student_controller.academic_course_service == mock_academic_course_service


class TestStudentControllerLoadStudents:
    """Tests per al mètode load_students del StudentController."""
    
    def test_load_students_calls_service(self, student_controller, mock_student_service):
        """Verifica que load_students crida al servei."""
        mock_student_service.get_all.return_value = [
            Student(id=1, uuid="test-uuid", name="Test", surnames="User", group_name="4t A")
        ]
        
        result = student_controller.load_students()
        
        mock_student_service.get_all.assert_called_once()
        assert len(result) == 1
    
    def test_load_students_emits_signal(self, student_controller, mock_student_service):
        """Verifica que load_students emet el senyal students_loaded."""
        students = [Student(id=1, uuid="test-uuid", name="Test", surnames="User", group_name="4t A")]
        mock_student_service.get_all.return_value = students
        
        mock_slot = MagicMock()
        student_controller.students_loaded.connect(mock_slot)
        
        student_controller.load_students()
        
        mock_slot.assert_called_once_with(students)


class TestStudentControllerSearch:
    """Tests per al mètode search_students del StudentController."""
    
    def test_search_students_calls_service(self, student_controller, mock_student_service):
        """Verifica que search_students crida al servei."""
        query = "Test"
        mock_student_service.search.return_value = [
            Student(id=1, uuid="test-uuid", name="Test", surnames="User", group_name="4t A")
        ]
        
        result = student_controller.search_students(query)
        
        mock_student_service.search.assert_called_once_with(query)
        assert len(result) == 1


class TestStudentControllerGetStudent:
    """Tests per al mètode get_student del StudentController."""
    
    def test_get_student_calls_service(self, student_controller, mock_student_service):
        """Verifica que get_student crida al servei."""
        student_id = 1
        expected_student = Student(id=1, uuid="test-uuid", name="Test", surnames="User", group_name="4t A")
        mock_student_service.get_student_by_id.return_value = expected_student
        
        result = student_controller.get_student(student_id)
        
        mock_student_service.get_student_by_id.assert_called_once_with(student_id)
        assert result == expected_student
    
    def test_get_student_returns_none_when_not_found(self, student_controller, mock_student_service):
        """Verifica que get_student retorna None quan no es troba."""
        mock_student_service.get_student_by_id.return_value = None
        
        result = student_controller.get_student(999)
        
        assert result is None


class TestStudentControllerCreateStudent:
    """Tests per al mètode create_student del StudentController."""
    
    def test_create_student_calls_service(self, student_controller, mock_student_service):
        """Verifica que create_student crida al servei."""
        data = StudentNew(uuid="test-uuid", name="Test", surnames="User", group_name="4t A")
        expected_student = Student(id=1, uuid="test-uuid", name="Test", surnames="User", group_name="4t A")
        mock_student_service.create_student.return_value = expected_student
        
        result = student_controller.create_student(data)
        
        mock_student_service.create_student.assert_called_once_with(data)
        assert result == expected_student
    
    def test_create_student_emits_signal(self, student_controller, mock_student_service):
        """Verifica que create_student emet el senyal student_created."""
        data = StudentNew(uuid="test-uuid", name="Test", surnames="User", group_name="4t A")
        expected_student = Student(id=1, uuid="test-uuid", name="Test", surnames="User", group_name="4t A")
        mock_student_service.create_student.return_value = expected_student
        
        mock_slot = MagicMock()
        student_controller.student_created.connect(mock_slot)
        
        student_controller.create_student(data)
        
        mock_slot.assert_called_once_with(expected_student)


class TestStudentControllerDeleteStudent:
    """Tests per al mètode delete_student del StudentController."""
    
    def test_delete_student_calls_service(self, student_controller, mock_student_service):
        """Verifica que delete_student crida al servei."""
        student_id = 1
        mock_student_service.delete.return_value = None
        
        result = student_controller.delete_student(student_id)
        
        mock_student_service.delete.assert_called_once_with(student_id)
        assert result is True
    
    def test_delete_student_emits_signal(self, student_controller, mock_student_service):
        """Verifica que delete_student emet el senyal student_deleted."""
        student_id = 1
        mock_student_service.delete.return_value = None
        
        mock_slot = MagicMock()
        student_controller.student_deleted.connect(mock_slot)
        
        student_controller.delete_student(student_id)
        
        mock_slot.assert_called_once_with(student_id)
    
    def test_delete_student_returns_false_on_exception(self, student_controller, mock_student_service):
        """Verifica que delete_student retorna False en cas d'error."""
        student_id = 1
        mock_student_service.delete.side_effect = Exception("Error")
        
        result = student_controller.delete_student(student_id)
        
        assert result is False
