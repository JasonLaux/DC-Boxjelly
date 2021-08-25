import pathlib
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
        meta = pathlib.Path(path).read_text().strip().splitlines()
        self.assertListEqual(meta, value)


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
        jobs = list(models.Job) # type: ignore
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

        self.assertEqual(j.client_address_1, None)
        self.assertMetaContent('data/jobs/1/meta.ini', [
            '[DEFAULT]',
            'client_name = A client',
        ])

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


if __name__ == '__main__':
    unittest.main()
