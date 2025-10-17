#!/usr/bin/env python
# encoding: utf-8
"""
reader.py

Created by David Peckham on 2009-09-07.
Copyright (c) 2009 David Peckham. All rights reserved.

Enhanced by Sanjay Sharma (indoos@gmail.com) 2025-10-17.
"""

import datetime
import os
import pdb
import struct
import sys

sys.path.insert(0, '..')
from pyunv.universe import Universe, Parameters, Class, Join, Object
from pyunv.universe import Condition, Table, VirtualTable, Column, Context, Link, Hierarchy

# import pyunv

class Reader(object):
    
    _content_markers = ('Objects;', 'Tables;', 'Columns;', 'Contexts;',
        'Virtual Tables;', 'Parameters;', 'Columns Id;', 'Joins;',
        'Links;', 'Hierarchies;', 'Parameters_6_0;', 'Parameters_4_1;',
        'Parameters_5_0;', 'Parameters_11_5;', 'Object_Formats;',
        'Object_ExtraFormats;', 'Dynamic_Class_Descriptions;',
        'Dynamic_Object_Descriptions;', 'Dynamic_Property_Descriptions;',
        'Audit;', 'Dimensions;', 'OLAPInfo;', 'Graphical_Info;',
        'Crystal_References;', 'XML-LOV;', 'Integrity;',
        'AggregateNavigation;', 'BoundedColumns;', 'BuildOrigin_v6;',
        'CompulsaryType;', 'Deleted References;', 'DELETED_HISTORY;',
        'Dot_Tables;', 'Downward;', 'FormatLocaleSort;', 'FormatVersion;',
        'Joins Extensions;', 'Key References;', 'KernelPageFormat;',
        'Platform;', 'UNICODE ON;', 'Upward;', 'Upward_LocalIndexing;',
        'Upward_Mapping;', 'Upward_Override;', 'Upward_Override_New;',
        'WindowsPageFormat;')
    
    def __init__(self, f):
        super(Reader, self).__init__()
        self.file = f
        self.find_content_offsets()
        self.universe = Universe()
        self.universe.parameters = self.read_parameters()
        self.universe.custom_parameters = self.read_customparameters()
        self.universe.tables = self.read_tables()
        self.universe.build_table_map()
        self.universe.virtual_tables = self.read_virtual_tables()
        self.universe.columns = self.read_columns()
        self.universe.columns.sort(key=lambda c: c.id_)
        #self.universe.column_attributes = self.read_column_attributes()
        self.universe.joins = self.read_joins()
        self.universe.contexts = self.read_contexts()
        self.universe.links = self.read_links()
        self.universe.hierarchies = self.read_hierarchies()
        # Read additional parameter versions
        try:
            self.universe.parameters_4_1 = self.read_parameters_4_1()
        except:
            self.universe.parameters_4_1 = None
        try:
            self.universe.parameters_5_0 = self.read_parameters_5_0()
        except:
            self.universe.parameters_5_0 = None
        try:
            self.universe.parameters_11_5 = self.read_parameters_11_5()
        except:
            self.universe.parameters_11_5 = None
        # Read formatting information
        try:
            self.universe.object_formats = self.read_object_formats()
        except:
            self.universe.object_formats = []
        try:
            self.universe.object_extra_formats = self.read_object_extra_formats()
        except:
            self.universe.object_extra_formats = []
        # Read dynamic descriptions
        try:
            self.universe.dynamic_class_descriptions = self.read_dynamic_class_descriptions()
        except:
            self.universe.dynamic_class_descriptions = {}
        try:
            self.universe.dynamic_object_descriptions = self.read_dynamic_object_descriptions()
        except:
            self.universe.dynamic_object_descriptions = {}
        try:
            self.universe.dynamic_property_descriptions = self.read_dynamic_property_descriptions()
        except:
            self.universe.dynamic_property_descriptions = {}
        # Read audit and metadata
        try:
            self.universe.audit_info = self.read_audit_info()
        except:
            self.universe.audit_info = None
        try:
            self.universe.dimensions = self.read_dimensions()
        except:
            self.universe.dimensions = []
        try:
            self.universe.olap_info = self.read_olap_info()
        except:
            self.universe.olap_info = None
        try:
            self.universe.graphical_info = self.read_graphical_info()
        except:
            self.universe.graphical_info = None
        try:
            self.universe.crystal_references = self.read_crystal_references()
        except:
            self.universe.crystal_references = []
        try:
            self.universe.xml_lov = self.read_xml_lov()
        except:
            self.universe.xml_lov = None
        try:
            self.universe.integrity_rules = self.read_integrity_rules()
        except:
            self.universe.integrity_rules = []
        # Read additional metadata sections
        try:
            self.universe.aggregate_navigation = self.read_aggregate_navigation()
        except:
            self.universe.aggregate_navigation = None
        try:
            self.universe.bounded_columns = self.read_bounded_columns()
        except:
            self.universe.bounded_columns = []
        try:
            self.universe.build_origin_v6 = self.read_build_origin_v6()
        except:
            self.universe.build_origin_v6 = None
        try:
            self.universe.compulsary_type = self.read_compulsary_type()
        except:
            self.universe.compulsary_type = None
        try:
            self.universe.deleted_references = self.read_deleted_references()
        except:
            self.universe.deleted_references = []
        try:
            self.universe.deleted_history = self.read_deleted_history()
        except:
            self.universe.deleted_history = []
        try:
            self.universe.dot_tables = self.read_dot_tables()
        except:
            self.universe.dot_tables = []
        try:
            self.universe.downward = self.read_downward()
        except:
            self.universe.downward = None
        try:
            self.universe.format_locale_sort = self.read_format_locale_sort()
        except:
            self.universe.format_locale_sort = None
        try:
            self.universe.format_version = self.read_format_version()
        except:
            self.universe.format_version = None
        try:
            self.universe.joins_extensions = self.read_joins_extensions()
        except:
            self.universe.joins_extensions = []
        try:
            self.universe.key_references = self.read_key_references()
        except:
            self.universe.key_references = []
        try:
            self.universe.kernel_page_format = self.read_kernel_page_format()
        except:
            self.universe.kernel_page_format = None
        try:
            self.universe.platform = self.read_platform()
        except:
            self.universe.platform = None
        try:
            self.universe.unicode_on = self.read_unicode_on()
        except:
            self.universe.unicode_on = None
        try:
            self.universe.upward = self.read_upward()
        except:
            self.universe.upward = None
        try:
            self.universe.upward_local_indexing = self.read_upward_local_indexing()
        except:
            self.universe.upward_local_indexing = None
        try:
            self.universe.upward_mapping = self.read_upward_mapping()
        except:
            self.universe.upward_mapping = None
        try:
            self.universe.upward_override = self.read_upward_override()
        except:
            self.universe.upward_override = None
        try:
            self.universe.upward_override_new = self.read_upward_override_new()
        except:
            self.universe.upward_override_new = None
        try:
            self.universe.windows_page_format = self.read_windows_page_format()
        except:
            self.universe.windows_page_format = None
        self.universe.classes = self.read_classes()

    def find_content_offsets(self):
        """find the offsets of the object, table, and column definitions 
        in the BusinessObjects universe file.
        
        In some universe files, the markers appear more than once. In most
        cases, the first occurence is the right one. One exception is when
        the marker recurs almost immediately -- in this case we need to skip
        over the false marker and search the rest of the file.
        """
        
        self.content_offsets = dict()
        contents = self.file.read()
        for marker in Reader._content_markers:
            marker_bytes = b'\x00' + marker.encode('utf-8')
            begin = contents.find(marker_bytes)
            end = begin + len(marker_bytes)
            if contents.find(marker.encode('utf-8'), begin-20, begin) != -1 or \
                    contents.find(marker.encode('utf-8'), end, end+20) != -1:
                begin = contents.find(marker_bytes, end+20)
                end = begin + len(marker_bytes)
            self.content_offsets[marker] = end
        del contents
        return
    
    def read_parameters(self):
        """docstring for read_parameters
        
        I unknown (usually 0x22)
        I unknown
        S universe_filename
        S universe_name
        I revision
        H unknown
        S description
        S created_by
        S modified_by
        I created_date
        I modified_date
        I query_time_limit (seconds)
        I query_row_limit
        S unknown
        S object_strategy
        x unknown
        I cost_estimate_warning_limit (seconds)
        I long_text_limit (characters)
        4x unknown
        S comments
        3I unknown
        S domain
        S dbms_engine
        S network_layer
        
         Other parameter blocks we don't parse yet:
            Parameters_4_1;
            Parameters_5_0;
            Parameters_6_0;
            Parameters_11_5;
        
        """
        self.file.seek(self.content_offsets['Parameters;'])
        params = Parameters()
        struct.unpack('<2I', self.file.read(8))
        params.universe_filename = self.read_string()
        params.universe_name = self.read_string()
        params.revision, = struct.unpack('<I', self.file.read(4))
        struct.unpack('<H', self.file.read(2))
        params.description = self.read_string()
        params.created_by = self.read_string()
        params.modified_by = self.read_string()
        created, modified, = struct.unpack('<2I', self.file.read(8))
        params.created_date = Reader.date_from_dateindex(created)
        params.modified_date = Reader.date_from_dateindex(modified)
        seconds, = struct.unpack('<I', self.file.read(4))
        params.query_time_limit = seconds / 60
        params.query_row_limit, = struct.unpack('<I', self.file.read(4))
        self.read_string()
        params.object_strategy = self.read_string()
        struct.unpack('<x', self.file.read(1))
        seconds, = struct.unpack('<I', self.file.read(4))
        params.cost_estimate_warning_limit = seconds / 60
        params.long_text_limit, = struct.unpack('<I', self.file.read(4))
        struct.unpack('<4x', self.file.read(4))
        params.comments = self.read_string()
        struct.unpack('<3I', self.file.read(12))
        params.domain = self.read_string()
        params.dbms_engine = self.read_string()
        params.network_layer = self.read_string()
        return params
    
    def read_customparameters(self):
        """read the parameters defined on the Parameter tab of the 
        Designer Parameters dialog
        
        I count
        array of parameters:
            S universe_filename
            S universe_name
        
         Other parameter blocks we don't parse yet:
            Parameters_4_1;
            Parameters_5_0;
            Parameters_11_5;
        
        """
        self.file.seek(self.content_offsets['Parameters_6_0;'])
        params = dict()
        count, = struct.unpack('<I', self.file.read(4))
        for p in range(count):
            name = self.read_string()
            value = self.read_string()
            params[name] = value
        return params

    def read_tables(self):
        """read a BusinessObjects schema definition from the universe file

        B unknown (usually 0x1)
        B unknown (usually 0x1 or 0x2)
        S database_username?
        S schema_name
        I max_table_id
        I table_count
        ???B tables

        """
        self.file.seek(self.content_offsets['Tables;'])
        # pdb.set_trace()
        self.file.read(2)
        user_name = self.read_string()
        schema = self.read_string()
        max_table_id, = struct.unpack('<I', self.file.read(4))
        table_count, = struct.unpack('<I', self.file.read(4))
        return [self.read_table(schema) for x in range(table_count)]

    def read_virtual_tables(self):
        """read the virtual table definitions from the universe file

        I virtual_table_count
        ???B virtual_tables

        """
        self.file.seek(self.content_offsets['Virtual Tables;'])
        count, = struct.unpack('<I', self.file.read(4))
        return [self.read_virtualtable() for x in range(count)]

    def read_columns(self):
        """read the list of source database columns from the universe file

        I column_count
        I column_count?
        ???B columns

        """
        self.file.seek(self.content_offsets['Columns Id;'])
        column_count, = struct.unpack('<I', self.file.read(4))
        column_count2, = struct.unpack('<I', self.file.read(4))
        #print('count1 %d  count2 %d' % (column_count, column_count2))
        return [self.read_column() for x in range(column_count2)]
    
    def read_column_attributes(self):
        """read the column attributes (after marker Columns;)"""
        pass

    def read_joins(self):
        """docstring for read_joins
        
        I table_count?
        I unknown
        I join_count
        [...joins...]
        I unknown

        """
        self.file.seek(self.content_offsets['Joins;'])
        self.file.read(8)
        join_count, = struct.unpack('<I', self.file.read(4))
        joins = [self.read_join() for x in range(join_count)]
        self.file.read(8)
        return joins

    def read_contexts(self):
        """docstring for read_contexts
        
        I max_context_id?
        I context_count
        contexts...

        """
        self.file.seek(self.content_offsets['Contexts;'])
        # pdb.set_trace()
        max_id, = struct.unpack('<I', self.file.read(4))
        count, = struct.unpack('<I', self.file.read(4))
        contexts = [self.read_context() for x in range(count)]
        return contexts

    def read_links(self):
        """docstring for read_links
        
        I max_link_id?
        I link_count
        links...

        """
        self.file.seek(self.content_offsets['Links;'])
        max_id, = struct.unpack('<I', self.file.read(4))
        count, = struct.unpack('<I', self.file.read(4))
        links = [self.read_link() for x in range(count)]
        return links

    def read_hierarchies(self):
        """docstring for read_hierarchies
        
        I max_hierarchy_id?
        I hierarchy_count
        hierarchies...

        """
        self.file.seek(self.content_offsets['Hierarchies;'])
        max_id, = struct.unpack('<I', self.file.read(4))
        count, = struct.unpack('<I', self.file.read(4))
        hierarchies = [self.read_hierarchy() for x in range(count)]
        return hierarchies

    def read_classes(self):
        """docstring for read_classes"""
        self.file.seek(self.content_offsets['Objects;'])
        class_count, object_count, condition_count, rootclass_count, = \
            struct.unpack('<4I', self.file.read(16))
        return [self.read_class(None) for x in range(rootclass_count)]
        
    def read_table(self, schema):
        """read a table definition from the universe file

        I table_id
        7x
        3I unknown
        S table_name
        I parent_id
        9x
        ? flag
            H count
            xxI unknown (count times)
        
        """
        id_, = struct.unpack('<I', self.file.read(4))
        self.file.read(19)
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        self.file.read(9)
        flag, = struct.unpack('<?', self.file.read(1))
        if flag:
            count, = struct.unpack('<H', self.file.read(2))
            self.file.read(4*count+3)
        else:
            self.file.read(1)
        return Table(self.universe, id_, parent_id, name, schema)

    def read_virtualtable(self):
        """read a virtual table definition from the universe file

        I table_id
        S select
        
        """
        table_id, = struct.unpack('<I', self.file.read(4))
        select = self.read_string()
        return VirtualTable(self.universe, table_id, select)

    def read_column(self):
        """read a column definition from the universe file

        I column_id
        I table_id
        S table_name
        
        """
        id_, = struct.unpack('<I', self.file.read(4))
        table_id, = struct.unpack('<I', self.file.read(4))
        parent = self.universe.table_map[table_id]
        name = self.read_string()
        #print(name)
        return Column(id_, name, parent, self.universe)

    def read_class(self, parent):
        """read a BusinessObjects class definition from the universe file

        I subclass_count
        I id
        S name
        I parent_id
        S description
        7B unknown
        I object_count
        ???B objects
        I condition_count
        ???B conditions
        ???B subclasses

        """
        id_, = struct.unpack('<I', self.file.read(4))
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        if parent:
            assert(parent_id==parent.id_)
        else:
            assert(parent_id == 0)
        description = self.read_string()
        c = Class(self.universe, id_, parent, name, description)
        self.file.seek(7, os.SEEK_CUR)
        object_count, = struct.unpack('<I', self.file.read(4))
        c.objects = [self.read_object(c) for x in range(object_count)]
        condition_count, = struct.unpack('<I', self.file.read(4))
        c.conditions = [self.read_condition(c) for x in range(condition_count)]
        subclass_count, = struct.unpack('<I', self.file.read(4))
        c.subclasses = [self.read_class(c) for x in range(subclass_count)]
        return c

    def read_object(self, parent):
        """read a BusinessObjects object definition from the universe file

        I id
        S name
        I parent_id
        S description
        H select_table_count
        ?I select_table_ids (repeats select_table_count times)
        H where_table_count
        ?I where_table_ids (repeats where_table_count times)
        S select (starts 03 nn* 2E)
        S where (starts 02 nn* 20)
        S format
        S unknown
        S lov_name
        2x unknown
        x visibility (show=0x36, hidden=0x76)
        55B unknown  (LOV settings, hide indicator?)

       """
        id_, = struct.unpack('<I', self.file.read(4))
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        if parent:
            assert(parent_id==parent.id_)
        else:
            assert(parent_id == 0)
        description = self.read_string()
        o = Object(self.universe, id_, parent, name, description)
        select_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % select_tablecount, 
            self.file.read(4 * select_tablecount))
        where_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % where_tablecount, 
            self.file.read(4 * where_tablecount))
        o.select = self.read_string()
        o.where = self.read_string()
        o.format = self.read_string()
        unknown2 = self.read_string()
        o.lov_name = self.read_string()
        self.file.seek(2, os.SEEK_CUR)
        visibility, = struct.unpack('<B', self.file.read(1))
        o.visible = visibility != 0x36
        self.file.seek(55, os.SEEK_CUR)
        return o

    def read_condition(self, parent):
        """read a BusinessObjects condition definition from 
        the universe file

        I id
        S name
        I parent_id
        S description
        H where_tablecount
        ?I where_table_ids (repeats where_tablecount times)
        H unknown_tablecount
        ?I table_ids (repeats unknown_tablecount times)
        S where

        """
        id_, = struct.unpack('<I', self.file.read(4))
        name = self.read_string()
        parent_id, = struct.unpack('<I', self.file.read(4))
        if parent:
            assert(parent_id==parent.id_)
        else:
            assert(parent_id == 0)
        description = self.read_string()
        c = Condition(self.universe, id_, parent, name, description)
        where_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % where_tablecount, 
            self.file.read(4 * where_tablecount))
        unknown_tablecount, = struct.unpack('<H', self.file.read(2))
        struct.unpack('<%dI' % unknown_tablecount, 
            self.file.read(4 * unknown_tablecount))
        c.where = self.read_string()
        return c

    def read_join(self):
        """read a BusinessObjects join definition from the universe file

        I join_id
        5I unknown
        S join_conditions
        2I unknown
        I term_count
        [repeats term_count times]
            S term
            I term_table_id

        """
        join_id, = struct.unpack('<I', self.file.read(4))
        self.file.read(20)
        j = Join(self.universe, join_id)
        j.expression = self.read_string()
        self.file.read(8)
        j.term_count, = struct.unpack('<I', self.file.read(4))
        j.terms = []
        for i in range(j.term_count):
            term_name = self.read_string()
            term_parent_id, = struct.unpack('<I', self.file.read(4)) 
            j.terms.append((term_name, term_parent_id))
        return j

    def read_context(self):
        """read a BusinessObjects context definition from the universe file

        S name
        I id
        S description
        I join_count
        [repeats join_count times]
            join_id

        """
        name = self.read_string()
        id_, = struct.unpack('<I', self.file.read(4))
        description = self.read_string()
        c = Context(self.universe, id_, name, description)
        join_count, = struct.unpack('<I', self.file.read(4))
        for i in range(join_count):
            join_id, = struct.unpack('<I', self.file.read(4))
            c.joins.append(join_id)
        return c

    def read_link(self):
        """read a BusinessObjects link definition from the universe file

        S name
        I id
        S description
        S linked_universe

        """
        name = self.read_string()
        id_, = struct.unpack('<I', self.file.read(4))
        description = self.read_string()
        linked_universe = self.read_string()
        l = Link(self.universe, id_, name, description, linked_universe)
        return l

    def read_hierarchy(self):
        """read a BusinessObjects hierarchy definition from the universe file

        S name
        I id
        S description
        I level_count
        [repeats level_count times]
            I level_object_id

        """
        name = self.read_string()
        id_, = struct.unpack('<I', self.file.read(4))
        description = self.read_string()
        h = Hierarchy(self.universe, id_, name, description)
        level_count, = struct.unpack('<I', self.file.read(4))
        for i in range(level_count):
            level_id, = struct.unpack('<I', self.file.read(4))
            h.levels.append(level_id)
        return h

    def read_string(self):
        """read a variable-length string from the universe file"""
        length, = struct.unpack('<H', self.file.read(2))
        if length:
            s, = struct.unpack('<%ds' % length, self.file.read(length))
            return s.translate(None, b'\x0d\x0a').decode('utf-8', errors='ignore')
        else:
            return None

    @classmethod
    def date_from_dateindex(cls, dateindex):
        """return the date corresponding to the BusinessObjects 
        universe date index"""
        assert dateindex >= 2442964, 'dateindex must be <= 2442964'
        return datetime.date(1976, 7, 4) + \
            datetime.timedelta(dateindex-2442964)

    # Additional parsing methods for enhanced universe information

    def read_parameters_4_1(self):
        """Read Parameters_4_1 section"""
        if 'Parameters_4_1;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Parameters_4_1;'])
        # Read the binary data
        length = self._get_section_length('Parameters_4_1;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_parameters_5_0(self):
        """Read Parameters_5_0 section"""
        if 'Parameters_5_0;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Parameters_5_0;'])
        length = self._get_section_length('Parameters_5_0;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_parameters_11_5(self):
        """Read Parameters_11_5 section"""
        if 'Parameters_11_5;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Parameters_11_5;'])
        length = self._get_section_length('Parameters_11_5;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_object_formats(self):
        """Read Object_Formats section"""
        if 'Object_Formats;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Object_Formats;'])
        length = self._get_section_length('Object_Formats;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_object_extra_formats(self):
        """Read Object_ExtraFormats section"""
        if 'Object_ExtraFormats;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Object_ExtraFormats;'])
        length = self._get_section_length('Object_ExtraFormats;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_dynamic_class_descriptions(self):
        """Read Dynamic_Class_Descriptions section"""
        if 'Dynamic_Class_Descriptions;' not in self.content_offsets:
            return {}
        self.file.seek(self.content_offsets['Dynamic_Class_Descriptions;'])
        length = self._get_section_length('Dynamic_Class_Descriptions;')
        if length > 0:
            return self.file.read(length)
        return {}

    def read_dynamic_object_descriptions(self):
        """Read Dynamic_Object_Descriptions section"""
        if 'Dynamic_Object_Descriptions;' not in self.content_offsets:
            return {}
        self.file.seek(self.content_offsets['Dynamic_Object_Descriptions;'])
        length = self._get_section_length('Dynamic_Object_Descriptions;')
        if length > 0:
            return self.file.read(length)
        return {}

    def read_dynamic_property_descriptions(self):
        """Read Dynamic_Property_Descriptions section"""
        if 'Dynamic_Property_Descriptions;' not in self.content_offsets:
            return {}
        self.file.seek(self.content_offsets['Dynamic_Property_Descriptions;'])
        length = self._get_section_length('Dynamic_Property_Descriptions;')
        if length > 0:
            return self.file.read(length)
        return {}

    def read_audit_info(self):
        """Read Audit information"""
        if 'Audit;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Audit;'])
        length = self._get_section_length('Audit;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_dimensions(self):
        """Read Dimensions section"""
        if 'Dimensions;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Dimensions;'])
        length = self._get_section_length('Dimensions;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_olap_info(self):
        """Read OLAP information"""
        if 'OLAPInfo;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['OLAPInfo;'])
        length = self._get_section_length('OLAPInfo;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_graphical_info(self):
        """Read Graphical information"""
        if 'Graphical_Info;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Graphical_Info;'])
        length = self._get_section_length('Graphical_Info;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_crystal_references(self):
        """Read Crystal References"""
        if 'Crystal_References;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Crystal_References;'])
        length = self._get_section_length('Crystal_References;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_xml_lov(self):
        """Read XML LOV information"""
        if 'XML-LOV;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['XML-LOV;'])
        length = self._get_section_length('XML-LOV;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_integrity_rules(self):
        """Read Integrity rules"""
        if 'Integrity;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Integrity;'])
        length = self._get_section_length('Integrity;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_aggregate_navigation(self):
        """Read Aggregate Navigation information"""
        if 'AggregateNavigation;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['AggregateNavigation;'])
        length = self._get_section_length('AggregateNavigation;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_bounded_columns(self):
        """Read Bounded Columns information"""
        if 'BoundedColumns;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['BoundedColumns;'])
        length = self._get_section_length('BoundedColumns;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_build_origin_v6(self):
        """Read Build Origin V6 information"""
        if 'BuildOrigin_v6;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['BuildOrigin_v6;'])
        length = self._get_section_length('BuildOrigin_v6;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_compulsary_type(self):
        """Read Compulsary Type information"""
        if 'CompulsaryType;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['CompulsaryType;'])
        length = self._get_section_length('CompulsaryType;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_deleted_references(self):
        """Read Deleted References"""
        if 'Deleted References;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Deleted References;'])
        length = self._get_section_length('Deleted References;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_deleted_history(self):
        """Read Deleted History"""
        if 'DELETED_HISTORY;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['DELETED_HISTORY;'])
        length = self._get_section_length('DELETED_HISTORY;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_dot_tables(self):
        """Read Dot Tables information"""
        if 'Dot_Tables;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Dot_Tables;'])
        length = self._get_section_length('Dot_Tables;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_downward(self):
        """Read Downward information"""
        if 'Downward;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Downward;'])
        length = self._get_section_length('Downward;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_format_locale_sort(self):
        """Read Format Locale Sort information"""
        if 'FormatLocaleSort;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['FormatLocaleSort;'])
        length = self._get_section_length('FormatLocaleSort;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_format_version(self):
        """Read Format Version information"""
        if 'FormatVersion;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['FormatVersion;'])
        length = self._get_section_length('FormatVersion;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_joins_extensions(self):
        """Read Joins Extensions"""
        if 'Joins Extensions;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Joins Extensions;'])
        length = self._get_section_length('Joins Extensions;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_key_references(self):
        """Read Key References"""
        if 'Key References;' not in self.content_offsets:
            return []
        self.file.seek(self.content_offsets['Key References;'])
        length = self._get_section_length('Key References;')
        if length > 0:
            return self.file.read(length)
        return []

    def read_kernel_page_format(self):
        """Read Kernel Page Format information"""
        if 'KernelPageFormat;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['KernelPageFormat;'])
        length = self._get_section_length('KernelPageFormat;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_platform(self):
        """Read Platform information"""
        if 'Platform;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Platform;'])
        length = self._get_section_length('Platform;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_unicode_on(self):
        """Read Unicode On information"""
        if 'UNICODE ON;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['UNICODE ON;'])
        length = self._get_section_length('UNICODE ON;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward(self):
        """Read Upward information"""
        if 'Upward;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward;'])
        length = self._get_section_length('Upward;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_local_indexing(self):
        """Read Upward Local Indexing information"""
        if 'Upward_LocalIndexing;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_LocalIndexing;'])
        length = self._get_section_length('Upward_LocalIndexing;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_mapping(self):
        """Read Upward Mapping information"""
        if 'Upward_Mapping;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_Mapping;'])
        length = self._get_section_length('Upward_Mapping;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_override(self):
        """Read Upward Override information"""
        if 'Upward_Override;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_Override;'])
        length = self._get_section_length('Upward_Override;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_upward_override_new(self):
        """Read Upward Override New information"""
        if 'Upward_Override_New;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['Upward_Override_New;'])
        length = self._get_section_length('Upward_Override_New;')
        if length > 0:
            return self.file.read(length)
        return None

    def read_windows_page_format(self):
        """Read Windows Page Format information"""
        if 'WindowsPageFormat;' not in self.content_offsets:
            return None
        self.file.seek(self.content_offsets['WindowsPageFormat;'])
        length = self._get_section_length('WindowsPageFormat;')
        if length > 0:
            return self.file.read(length)
        return None

    def _get_section_length(self, marker):
        """Helper method to calculate section length"""
        current_pos = self.file.tell()
        # Find the next marker or end of file
        next_markers = [m for m in self.content_offsets.keys() if self.content_offsets[m] > current_pos]
        if next_markers:
            next_pos = min(self.content_offsets[m] for m in next_markers)
            return next_pos - current_pos
        else:
            # Last section, read to end
            self.file.seek(0, 2)  # Seek to end
            end_pos = self.file.tell()
            self.file.seek(current_pos)
            return end_pos - current_pos
