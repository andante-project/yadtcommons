#   yadt_commons
#   Copyright (C) 2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


__author__ = 'Michael Gruber'

import unittest

from mock import Mock, call, patch

from yadt_commons.configuration import ConfigurationException, YadtConfigParser


try:
    import __builtin__
    builtins_string = '__builtin__'
except:
    import builtins
    builtins_string = 'builtins'

class YadtConfigParserTests (unittest.TestCase):
    def test_should_create_instance_of_YadtConfigParser(self):
        parser = YadtConfigParser()

        name_of_type = parser._parser.__class__.__name__
        self.assertEqual('SafeConfigParser', name_of_type)

    @patch('yadt_commons.configuration.sys')
    @patch('yadt_commons.configuration.os.path.exists')
    @patch(builtins_string + '.exit')
    def test_should_exit_when_configuration_file_does_not_exist(self, mock_exit, mock_exists, mock_log):
        mock_parser = Mock(YadtConfigParser)
        mock_exists.return_value = False

        YadtConfigParser.read_configuration_file(mock_parser, 'some.cfg')

        self.assertEqual(call('some.cfg'), mock_exists.call_args)
        self.assertEqual(call(1), mock_exit.call_args)

    @patch('yadt_commons.configuration.sys')
    @patch('yadt_commons.configuration.os.path.exists')
    def test_should_read_configuration_file (self, mock_exists, mock_log):
        mock_parser = Mock(YadtConfigParser)
        mock_wrapped_parser = Mock()
        mock_parser._parser = mock_wrapped_parser
        mock_exists.return_value = True

        YadtConfigParser.read_configuration_file(mock_parser, 'some.cfg')

        self.assertEqual(call(['some.cfg']), mock_wrapped_parser.read.call_args)

    def test_should_raise_exception_when_given_option_is_not_digit(self):
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = 'abcdef'

        self.assertRaises(ConfigurationException, YadtConfigParser.get_option_as_int, mock_parser, 'section', 'option', 'default_value')

    def test_should_return_default_when_option_not_available(self):
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = ''

        actual_option = YadtConfigParser.get_option_as_list(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual('default_value', actual_option)
        self.assertEqual(call('section', 'option', ''), mock_parser.get_option.call_args)

    def test_should_return_list_separated_by_comma(self):
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = ' abc, def,ghi,jkl   '

        actual_option = YadtConfigParser.get_option_as_list(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual(['abc', 'def', 'ghi', 'jkl'], actual_option)
        self.assertEqual(call('section', 'option', ''), mock_parser.get_option.call_args)

    def test_should_return_a_set (self):
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option_as_list.return_value = ['abc', 'def', 'ghi', 'jkl']

        actual_option = YadtConfigParser.get_option_as_set(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual(set(['abc', 'def', 'ghi', 'jkl']), actual_option)
        self.assertEqual(call('section', 'option', 'default_value'), mock_parser.get_option_as_list.call_args)

    def test_should_return_yes_as_boolean_value_true(self):
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = 'yes'

        actual_option = YadtConfigParser.get_option_as_yes_or_no_boolean(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual(True, actual_option)
        self.assertEqual(call('section', 'option', 'default_value'), mock_parser.get_option.call_args)

    def test_should_return_no_as_boolean_value_false (self):
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = 'no'

        actual_option = YadtConfigParser.get_option_as_yes_or_no_boolean(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual(False, actual_option)
        self.assertEqual(call('section', 'option', 'default_value'), mock_parser.get_option.call_args)

    def test_should_raise_exception_when_given_value_is_not_yes_or_no (self):
        mock_parser = Mock(YadtConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.get_option.return_value = 'tralala'
        mock_parser._parser = mock_wrapped_parser

        self.assertRaises(ConfigurationException, YadtConfigParser.get_option_as_yes_or_no_boolean, mock_parser, 'section', 'option', 'default_value')

    def test_should_return_option_from_section (self):
        mock_parser = Mock(YadtConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = True
        mock_wrapped_parser.has_option.return_value = True
        mock_wrapped_parser.get.return_value = 'the option'
        mock_parser._parser = mock_wrapped_parser

        actual_option = YadtConfigParser.get_option(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual('the option', actual_option)
        self.assertEqual(call('section', 'option'), mock_wrapped_parser.has_option.call_args)
        self.assertEqual(call('section', 'option'), mock_wrapped_parser.get.call_args)

    def test_should_return_default_value_when_option_not_in_section (self):
        mock_parser = Mock(YadtConfigParser)
        mock_wrapped_parser = Mock()
        mock_wrapped_parser.has_section.return_value = True
        mock_wrapped_parser.has_option.return_value = False
        mock_parser._parser = mock_wrapped_parser

        actual_option = YadtConfigParser.get_option(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual('default_value', actual_option)
        self.assertEqual(call('section', 'option'), mock_wrapped_parser.has_option.call_args)

    def test_should_return_option_as_int (self):
        mock_parser = Mock(YadtConfigParser)
        mock_parser.get_option.return_value = '123456'

        actual_option = YadtConfigParser.get_option_as_int(mock_parser, 'section', 'option', 'default_value')

        self.assertEqual(123456, actual_option)
        self.assertEqual(call('section', 'option', 'default_value'), mock_parser.get_option.call_args)
