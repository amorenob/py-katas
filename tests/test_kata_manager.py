"""
Tests for kata management functionality
"""

import pytest
from pathlib import Path
from pykatas.kata_manager import load_katas, KATAS
from pykatas.models import Kata


class TestKataManager:
    """Test cases for kata loading and management"""

    def test_load_katas_returns_list(self):
        """Test that load_katas returns a list"""
        katas = load_katas()
        assert isinstance(katas, list)

    def test_load_katas_structure(self):
        """Test that loaded katas have correct structure"""
        katas = load_katas()
        assert len(katas) > 0

        for kata in katas:
            assert isinstance(kata, Kata)
            assert hasattr(kata, 'id')
            assert hasattr(kata, 'title')
            assert hasattr(kata, 'description')
            assert hasattr(kata, 'starter_code')

            # Check that fields are not empty
            assert len(kata.id) > 0
            assert len(kata.title) > 0
            assert len(kata.description) > 0
            assert len(kata.starter_code) > 0

    def test_katas_global_variable(self):
        """Test that KATAS global variable is populated"""
        assert isinstance(KATAS, list)
        assert len(KATAS) > 0


