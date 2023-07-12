from django.test import TestCase
import unittest

# Create your tests here.
from . import data_processing

# Test getFileRow function
def test_minimum():
    result = data_processing.getFileRow(2)
    assert result == ["file 0", "", "file 1", ""]


def test_five():
    result = data_processing.getFileRow(["file 0", "file 1", "file 2", "file 3", "file 4"])
    assert result == ["file 0", "", "file 1", "", "file 2", "", "file 3", "", "file 4", ""]

# Test checkSameCode function
def test_always_true():
    testList = [5, 2, 1, 2, 4, 2, 6, 2]
    result = data_processing.checkSameVersion(testList)
    assert result is True


def test_Same_Version_words():
    testList = ["245", "C1", "21d", "C1", "nsndbf", "C1"]
    result = data_processing.checkSameVersion(testList)
    assert result is True


def test_Same_Version_False():
    testList = [2, 5, 6, 1, 4, 7, 3]
    result = data_processing.checkSameVersion(testList)
    assert result is False


def test_Same_Code_True():
    testList = [5, 1, 5, 2, 5, 7, 5, 2]
    result = data_processing.checkSameCode(testList)
    assert result is True

def test_Same_Code_False():
    testList = [4, 5, 7, 1, 2, 4, 8, 10]
    result = data_processing.checkSameCode(testList)
    assert result is False


def test_prepare_Table():
    result = data_processing.prepareTable(3)
    assert result == ["Code", "Version", "Code", "Version", "Code", "Version", "Ref"]


