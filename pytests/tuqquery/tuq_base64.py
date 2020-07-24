import base64

from membase.api.exception import CBQError
from remote.remote_util import RemoteMachineShellConnection
from tuqquery.tuq import QueryTests


class Base64Tests(QueryTests):
    def setUp(self):
        self.skip_generation = True
        super(Base64Tests, self).setUp()
        self.gens_load = self.gen_docs(type='base64')
        for bucket in self.buckets:
            self.cluster.bucket_flush(self.main, bucket=bucket, timeout=self.wait_timeout * 5)
        self.load(self.gens_load)
        self.query_buckets = self.get_query_buckets(check_all_buckets=True)

    def suite_setUp(self):
        super(Base64Tests, self).suite_setUp()

    def tearDown(self):
        super(Base64Tests, self).tearDown()

    def suite_tearDown(self):
        super(Base64Tests, self).suite_tearDown()

    def test_simple_query(self):
        for query_bucket in self.query_buckets:
            try:
                self.query = "select BASE64(d) from %s as d" % query_bucket
                self.run_cbq_query()
                self.sleep(3)
                actual_result = self.run_cbq_query()
                actual_result = [doc["$1"] for doc in actual_result['results']]
                expected_result = self._generate_full_docs_list_base64(self.gens_load)
                expected_result = [base64.b64encode(doc.encode()) for doc in expected_result]
                self._verify_results_base64(actual_result, expected_result)
            except Exception as ex:
                self.query = "SELECT d FROM %s as d" % query_bucket
                self.run_cbq_query()
                raise ex

    def test_negative_value(self):
        # tuq should not crash after error
        for query_bucket in self.query_buckets:
            self.query = "select BASE64() from %s" % query_bucket
            try:
                self.run_cbq_query()
            except CBQError:
                shell = RemoteMachineShellConnection(self.main)
                output = shell.execute_command('ps -aef | grep cbq')
                if str(output).find('cbq-engine') == -1:
                    os = self.shell.extract_remote_info().type.lower()
                    if os != 'windows':
                        self.fail('Cbq-engine is crashed')
                self.log.info('Error appeared as expected')
            else:
                self.fail('Error expected but not appeared')
