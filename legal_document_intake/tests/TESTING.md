# Testing Documentation

This document explains the testing strategy and structure for the Legal Document Intake System.

## 📋 Test Suite Overview

The test suite is designed to demonstrate professional testing practices for AI-powered applications. It includes both working tests and educational examples of tests that would be implemented in a production environment.

## 🧪 Test Categories

### 1. **Core Unit Tests** (Active)
- **Document Processing**: Tests for PDF/document handling
- **API Endpoints**: FastAPI route validation
- **Data Validation**: Pydantic model testing
- **Service Initialization**: Component startup tests

### 2. **Integration Tests** (Active)
- **Health Checks**: System status validation
- **File Upload**: Basic upload functionality
- **Error Handling**: Invalid input handling

### 3. **Skipped Tests** (Future Implementation)
These tests are skipped as they require additional implementation or setup:

#### PDF Generation Tests
```python
@pytest.skip("Requires complete EmploymentContract data model")
def test_generate_employment_contract_pdf():
    # Test PDF generation with complete data models
    pass
```

#### AI Integration Tests
```python
@pytest.skip("Requires complete payslip sample data")
def test_extract_payslip_data():
    # Test AI-powered data extraction
    pass
```

#### Workflow Integration Tests
```python
@pytest.skip("Requires end-to-end workflow implementation")
def test_complete_workflow_employment_contract():
    # Test complete document processing workflow
    pass
```

## 🎯 Why Keep Skipped Tests?

### Development Planning
- **Roadmap**: Shows what needs to be implemented
- **Test Coverage**: Indicates comprehensive testing strategy
- **Future Work**: Easy to enable when features are ready

### Professional Practice
- **Realistic Approach**: Not all tests work immediately
- **Clear Planning**: Shows thoughtful test design
- **Maintainability**: Clean separation of working vs planned tests

## 🚀 Running Tests

### All Tests
```bash
python run_tests.py
```

### Specific Categories
```bash
# Run only working tests
python -m pytest tests/ -v

# Run only unit tests
python -m pytest tests/test_document_processing.py -v

# Run only API tests
python -m pytest tests/test_api_endpoints.py -v

# Skip API key required tests
python -m pytest tests/ -v -m "not skipif"
```

### Test Output Explanation
- **PASSED**: Test works correctly
- **FAILED**: Test found an issue (needs fixing)
- **SKIPPED**: Educational test (intentionally disabled)

## 📊 Test Results Interpretation

### Successful Run Example
```
✅ 15 passed
❌ 2 failed  
⏭️ 9 skipped
```

This indicates:
- **15 core features** are working correctly
- **2 issues** need attention
- **9 educational examples** are documented

### Common Skip Reasons
1. **Requires API Key**: Tests that need OpenAI integration
2. **Requires Full Models**: Tests needing complete data validation
3. **Requires File Processing**: Tests needing real document handling
4. **Requires Complex Setup**: Tests needing external dependencies

## 🔧 Enabling Skipped Tests

To enable a skipped test for actual use:

1. **Remove the skip decorator**:
```python
# Before
@pytest.skip("Educational example")
def test_something():
    pass

# After
def test_something():
    pass
```

2. **Add proper setup**:
```python
def test_something():
    # Add real implementation
    result = actual_function()
    assert result == expected_value
```

3. **Add required fixtures**:
```python
@pytest.fixture
def sample_data():
    return create_test_data()
```

## 💡 Test Design Principles

### 1. **Separation of Concerns**
- Unit tests for individual components
- Integration tests for component interaction
- End-to-end tests for complete workflows

### 2. **Realistic Testing**
- Test real scenarios users will encounter
- Include edge cases and error conditions
- Test both success and failure paths

### 3. **Educational Value**
- Tests should teach how the system works
- Clear naming and documentation
- Examples of different testing approaches

### 4. **Maintainability**
- Tests should be easy to understand and modify
- Clear skip reasons for disabled tests
- Consistent structure across test files

## 🎓 Learning Opportunities

This test suite demonstrates:
- **Professional testing practices**
- **Pytest usage and features**
- **API testing with FastAPI**
- **Pydantic model validation**
- **Error handling strategies**
- **Test organization and structure**

Use this as a reference for implementing testing in your own projects!