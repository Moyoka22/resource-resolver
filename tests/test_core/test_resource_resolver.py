import io
import pathlib
import tempfile
import unittest

from resource_resolver import ResourceResolver, ResourceResolverError


class BasicResourceResolverTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.test_resolver = ResourceResolver()
        return super().setUpClass()

    def test_define_allows_definition_of_a_valid_file_url(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / 'test.txt'
            with p.open('w+') as f:
                f.write('abc')
            self.test_resolver.define('valid_file_url', f'file://{str(p)}')

    def test_define_allows_definition_of_a_valid_file_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / 'test.txt'
            with p.open('w+') as f:
                f.write('abc')
            self.test_resolver.define('valid_file_path', p)

    def test_define_allows_definition_of_a_valid_string_io_resource(self):
        self.test_resolver.define('valid_buffer', io.StringIO())


class ResourceResolverTestSuite(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.test_path = (pathlib.Path(self.tmp_dir.name) /
                          'test_file.txt').resolve()

        self.test_file_contents = 'Test text.'

        self.test_path.touch()
        with self.test_path.open(mode='w+') as f:
            f.write(self.test_file_contents)

        self.test_resolver = ResourceResolver()
        self.test_io_buffer = io.StringIO()
        self.test_io_buffer.write(self.test_file_contents)

        self.test_path2 = (pathlib.Path(self.tmp_dir.name) /
                           'test_file2.txt').resolve()
        self.test_path2.touch()
        with self.test_path2.open(mode='w+') as f:
            f.write(self.test_file_contents)

        self.temp_key = 'test_temp_key'
        self.file_url_key = 'test_file_url_key'
        self.file_path_key = 'test_file_path_key'

        self.test_resolver.define(self.temp_key, self.test_io_buffer)
        self.test_resolver.define(
            self.file_url_key, f'file://{str(self.test_path)}')
        self.test_resolver.define(self.file_path_key, self.test_path2)

    def tearDown(self):
        self.tmp_dir.cleanup()
        self.test_resolver.clear()

    def test_has_returns_true_if_a_resource_has_been_defined(self):
        self.assertTrue(self.test_resolver.has(self.temp_key))

    def test_has_returns_false_if_a_resource_has_not_been_defined(self):
        self.assertFalse(self.test_resolver.has('not'))

    def test_get_returns_expected_data_when_a_file_resource_is_defined(self):
        expected_result = self.test_file_contents
        received_result = self.test_resolver.get(self.file_path_key, as_a='file_handle')

        self.assertEqual(expected_result, received_result.read())
        
    def test_get_returns_expected_data_when_a_string_io_resource_is_defined(
            self):
        expected_result = self.test_file_contents
        received_result = self.test_resolver.get(self.temp_key)

        self.assertEqual(expected_result, received_result)

    def test_saved_data_returned_after_saving_to_file_resource(self):
        self.test_resolver.define('test2')

        content = 'abc123'

        self.test_resolver.save('test2', content)

        self.assertEqual(self.test_resolver.get('test2'), content)

    def test_saved_data_returned_after_saving_to_temporary_resource(self):
        content = 'abc123'
        self.test_resolver.save(self.temp_key, content)

        self.assertEqual(self.test_resolver.get(self.temp_key), content)

    def test_raises_undefined_resource_when_getting_resource_which_does_exist(
            self):
        with self.assertRaises(ResourceResolverError):
            self.test_resolver.get('doreme')

    def test_raises_duplicate_key_when_trying_define_a_resource_that_already_exists(
            self):
        with self.assertRaises(ResourceResolverError):
            self.test_resolver.define(self.temp_key, io.StringIO())

    def test_raises_error_for_unknown_protocol(self):
        with self.assertRaises(ResourceResolverError):
            self.test_resolver.define('abc', 'ftp://file-somewhere')

    def test_raises_error_for_undefined_get_as_a_format(self):
        with self.assertRaises(ResourceResolverError):
            self.test_resolver.get('test', as_a="abc") # type: ignore

    def test_returns_buffer_for_get_as_a_buffer_for_io_obj(self):
        buffer = self.test_resolver.get(self.temp_key, as_a="buffer")
        self.assertEqual(type(buffer), io.StringIO)

    def test_returns_buffer_for_get_as_a_buffer_for_file_obj(self):
        buffer = self.test_resolver.get(self.file_path_key, as_a="buffer")
        self.assertEqual(type(buffer), io.StringIO)

    def test_does_not_raises_duplicate_key_when_trying_define_a_resource_that_already_exists_using_overwrite(
            self):
        try:
            self.test_resolver.define('test2', io.StringIO(), overwrite=True)
        except ResourceResolverError as e:
            self.fail(e)

    def test_unsupported_write_type_throws_error(self):
        with self.assertRaises(ResourceResolverError):
            self.test_resolver.save('test', {})  # type: ignore

    def test_defining_a_resource_with_no_location_creates_an_in_memory_buffer(
            self):
        resolver = self.test_resolver

        resolver.define('abc123')

        contents = 'some contents...'

        resolver.save('abc123', contents)

        retrieved_value = resolver.get('abc123')

        self.assertEqual(retrieved_value, contents)

    def test_writing_to_one_buffer_does_not_affect_another(
            self):
        resolver = self.test_resolver

        contents = 'some contents...'
        contents2 = 'some contents2...'

        resolver.define('abc123')
        resolver.define('abc456')

        resolver.save('abc123', contents)
        resolver.save('abc456', contents2)

        self.assertEqual(resolver.get('abc123'), contents)

    def test_saving_to_a_read_only_resource_throws_an_error(
            self):
        resolver = self.test_resolver

        buffer = io.StringIO()
        contents = 'some contents...'

        buffer.write(contents)

        resolver.define('abc123', buffer, read_only=True)


        with self.assertRaises(ResourceResolverError):
            resolver.save('abc123', contents)


if __name__ == '__main__':
    unittest.main()