import datetime
from pathlib import Path
import unittest
import shutil
import importlib
import time_machine
import pytz
import filecmp
import logging

from app.core import definition, models

std_out_log = logging.StreamHandler()
std_out_log.setLevel(logging.DEBUG)
logging.basicConfig(handlers=[std_out_log, ])

class ModelTestBase(unittest.TestCase):
    def setUp(self) -> None:
        shutil.rmtree(definition.DATA_FOLDER)
        # creatate necessary folders
        importlib.reload(definition)
        importlib.reload(models)
        (definition.DATA_FOLDER / '.gitkeep').touch()

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

        # test create existed job
        self.assertRaises(ValueError, lambda: models.Job.make('2'))

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
        self.assertRegex(lines[1], r'^added_at = ')
        self.assertRegex(lines[2], r'^edited_at = ')
        self.assertEqual(lines[3], 'operator = Random Person')

    @time_machine.travel(datetime.datetime(2021, 1, 1, 12, 0, 0,
                                           tzinfo=pytz.timezone('Australia/Melbourne')))
    def test_raw_file(self):
        TEST_DATA_FOLDER = Path(__file__).parent / '_assert' / 'Data'
        CLIENT_A_RUN1_CLIENT = TEST_DATA_FOLDER / \
            'CAL00001 Raw ClientA-Run1-Client.csv'
        CLIENT_A_RUN1_LAB = TEST_DATA_FOLDER / \
            'CAL00001 Raw ClientA-Run1-Lab.csv'
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

        # test modifying meta data
        self.assertEqual(r.IC_HV, '-250')
        self.assertEqual(r.measured_at, '2021-02-12')
        self.assertEqual(r.operator, 'Duncan Butler')

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

        # test uploading lab raw data, it does not update meta data
        r.raw_lab.upload_from(CLIENT_A_RUN1_LAB)
        path = r.raw_lab.path
        assert path is not None

        self.assertEqual(r.IC_HV, '-250')

        # test import raw file with [DC_META] section
        r.raw_client.upload_from(EXPORTED_SNAPSHOT)
        r.raw_client.export_to(Path('data/test_exported.csv'))
        self.assertFileEqual(
            Path('data/test_exported.csv'), EXPORTED_SNAPSHOT)


class TestConstantFile(ModelTestBase):

    @time_machine.travel(datetime.datetime(2021, 1, 1, 12, 0, 0,
                                           tzinfo=pytz.timezone('Australia/Melbourne')))
    def test_CRUD(self):
        # assert no constants
        self.assertEqual(len(models.ConstantFile), 0)

        # read non-existing constant
        self.assertRaises(KeyError, lambda: models.ConstantFile[1])

        # create new constant and assert
        constant = models.ConstantFile.make()
        self.assertEqual(constant.id, 1)
        self.assertTrue(constant.path.samefile(
            'data/constants/1/constant.xlsx'))
        self.assertTrue(filecmp.cmp(
            constant.path, definition.TEMPLATE_CONSTANT_FILE))
        self.assertEqual(constant.added_at, '2021-01-01T13:20:00+11:00')
        self.assertIsNone(constant.note)

        # assert query
        self.assertEqual(len(models.ConstantFile), 1)
        self.assertTrue(1 in models.ConstantFile)
        self.assertEqual(models.ConstantFile[1].id, 1)
        for a in models.ConstantFile:
            self.assertEqual(a.id, 1)

        # assert delete
        del models.ConstantFile[1]
        # delete not existing object

        def rm():
            del models.ConstantFile[1]
        self.assertRaises(KeyError, rm)

    def test_default(self):
        # no default at start
        self.assertIsNone(models.constant_file_config.default_id)
        self.assertIsNone(models.constant_file_config.default)

        # set a default constent file
        f = models.ConstantFile.make()
        models.constant_file_config.default_id = f.id

        self.assertMetaContent('data/constants/meta.ini', [
            '[DEFAULT]',
            'default = 1',
        ])

        # get default constant
        default = models.constant_file_config.default
        self.assertIsNotNone(default)
        self.assertEqual(default.id, 1)  # type: ignore

        # file path
        self.assertTrue(models.constant_file_config.get_path()
            .samefile('data/constants/1/constant.xlsx'))

        # delete the file
        f.delete()
        self.assertIsNone(models.constant_file_config.default)
        self.assertMetaContent('data/constants/meta.ini', [
        ])

        # file path
        self.assertTrue(models.constant_file_config.get_path()
            .samefile('app/core/template_constant.xlsx'))

        # set a wrong default id
        models.constant_file_config.default_id = '42'
        # but it still reads None
        self.assertIsNone(models.constant_file_config.default)

        # file path
        self.assertTrue(models.constant_file_config.get_path()
            .samefile('app/core/template_constant.xlsx'))



if __name__ == '__main__':
    unittest.main()
