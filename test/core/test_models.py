from pathlib import Path
import unittest
import shutil
import importlib

from app.core import constraints, models


class ModelTestBase(unittest.TestCase):
    def setUp(self) -> None:
        shutil.rmtree(constraints.DATA_FOLDER)
        importlib.reload(constraints)  # creatate necessary folders
        (constraints.DATA_FOLDER / '.gitkeep').touch()

    def assertMetaContent(self, path, value: list):
        meta = Path(path).read_text().strip().splitlines()
        self.assertListEqual(meta, value)

    def assertFileEqual(self, left: Path, right: Path, msg=None):
        self.assertTrue(left.is_file(), f'{left} should be a file')
        self.assertTrue(right.is_file(), f'{right} should be a file')

        self.assertEqual(left.read_bytes(), right.read_bytes(), msg)


class TestJob(ModelTestBase):

    def test_CRUD(self):
        # assert no jobs
        self.assertEqual(len(models.Job), 0)

        # test add
        for i in range(1, 6):
            models.Job.make(str(i),
                            client_name=f'Client {i}',
                            client_address_1=f'{i}00 St')

        # test iter
        jobs = list(models.Job)  # type: ignore
        self.assertEqual(len(jobs), 5)
        self.assertEqual(jobs[0].client_name, 'Client 1')
        self.assertEqual(jobs[0].client_address_1, '100 St')

        # test get
        self.assertEqual(models.Job['1'].client_name, 'Client 1')
        self.assertEqual(models.Job['1'].client_address_1, '100 St')

        # test delete
        self.assertEqual(len(models.Job), 5)
        del models.Job['1']
        self.assertEqual(len(models.Job), 4)

        # test not existing key
        self.assertRaises(KeyError, lambda: models.Job['7'])

    def test_set_meta_data(self):
        j = models.Job.make('1')

        j.client_name = 'A client'
        j.client_address_1 = 'An address'

        self.assertEqual(j.client_name, 'A client')
        self.assertEqual(j.client_address_1, 'An address')
        self.assertMetaContent('data/jobs/1/meta.ini', [
            '[DEFAULT]',
            'client_name = A client',
            'client_address_1 = An address'
        ])

        del j.client_address_1

        self.assertIsNone(j.client_address_1)
        self.assertMetaContent('data/jobs/1/meta.ini', [
            '[DEFAULT]',
            'client_name = A client',
        ])

        # test meta dict
        self.assertDictEqual(j.meta, {
            'job_id': '1',
            'client_name': 'A client',
            'client_address_1': None,
            'client_address_2': None,
        })

    def test_modify_equipments(self):
        j = models.Job.make('1')

        # add
        j.add_equipment('AAA', '123')

        # iter
        for e in j:
            self.assertEqual(e.model, 'AAA')
            self.assertEqual(e.serial, '123')

        # contains
        self.assertTrue('AAA_123' in j)

        # len
        self.assertEqual(len(j), 1)

        # get
        e = j['AAA_123']
        self.assertEqual(e.model, 'AAA')
        self.assertEqual(e.serial, '123')

        # add equipments with same serial
        j.add_equipment('AAA', '456')
        self.assertRaises(ValueError, lambda: j.add_equipment('AAA', '456'))

        # delete
        del j['AAA_123']
        self.assertEqual(len(j), 1)


class TestMexRun(ModelTestBase):

    def test_meta_data(self):
        # get object
        job = models.Job.make('CAL0001')
        equipment = job.add_equipment('AAA', '123')
        r = equipment.mex.add()

        self.assertEqual(r.id, 1)

        # write meta data
        r.operator = 'Random Person'

        # read meta data
        self.assertEqual(r.operator, 'Random Person')

        # meta file
        lines = Path(
            'data/jobs/CAL0001/AAA_123/MEX/1/meta.ini').read_text().strip().splitlines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], '[DEFAULT]')
        self.assertRegexpMatches(lines[1], r'^added_at = ')
        self.assertRegexpMatches(lines[2], r'^edited_at = ')
        self.assertEqual(lines[3], 'operator = Random Person')

    def test_raw_file(self):
        TEST_DATA_FOLDER = Path(__file__).parent / '_assert' / 'Data'
        CLIENT_A_RUN1_CLIENT = TEST_DATA_FOLDER / \
            'CAL00001 Raw ClientA-Run1-Client.csv'
        EXPORTED_SNAPSHOT = Path(__file__).parent / \
            '_assert' / 'snapshots' / 'exported_raw_client.csv'

        # get object
        job = models.Job.make('CAL0001')
        equipment = job.add_equipment('AAA', '123')
        r = equipment.mex.add()

        # test client and lab object
        self.assertEqual(type(r.raw_client), type(r.raw_lab))

        # by default, you get None
        self.assertEqual(r.raw_client.path, None)

        # test adding file
        r.raw_client.upload_from(CLIENT_A_RUN1_CLIENT)
        path = r.raw_client.path
        assert path is not None

        self.assertTrue(path.samefile('data/jobs/CAL0001/AAA_123/MEX/1/raw/client.csv'),
                        'test the raw file path')
        self.assertFileEqual(path, CLIENT_A_RUN1_CLIENT, 'test file content')

        # test exporting
        r.raw_client.export_to(Path('data/test_exported.csv'))
        self.assertFileEqual(
            Path('data/test_exported.csv'), EXPORTED_SNAPSHOT)

        # test deleting
        r.raw_client.remove()
        self.assertFalse(
            Path('data/jobs/CAL0001/AAA_123/MEX/1/raw/client.csv').exists()
        )
        self.assertIsNone(r.raw_client.path)

        # test import raw file with [DC_META] section
        r.raw_client.upload_from(EXPORTED_SNAPSHOT)
        r.raw_client.export_to(Path('data/test_exported.csv'))
        self.assertFileEqual(
            Path('data/test_exported.csv'), EXPORTED_SNAPSHOT)


if __name__ == '__main__':
    unittest.main()
