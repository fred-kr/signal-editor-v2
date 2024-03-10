from .. import type_defs as _t
import typing as t
import polars as pl
from dataclasses import dataclass, field
from ..core.section import Section, SectionID
import weakref


class SectionController:
    def __init__(self) -> None:
        self._sections: weakref.WeakValueDictionary[SectionID, Section] = weakref.WeakValueDictionary()

    def add_section(self, section: Section) -> None:
        self._sections[section.section_id] = section

    def remove_section(self, section_id: SectionID) -> None:
        del self._sections[section_id]

    def get_section(self, section_id: SectionID) -> Section | None:
        return self._sections.get(section_id)