from datetime import datetime

from golem_messages.datastructures import p2p as dt_p2p
from golem_messages.factories.datastructures import p2p as dt_p2p_factory
from peewee import IntegrityError

import golem.model as m
from golem.testutils import DatabaseFixture

from tests.factories import model as m_factory


class TestBaseModel(DatabaseFixture):
    def test_utc(self):
        instance = m.GenericKeyValue.create(key='test')
        instance_copy = m.GenericKeyValue.get()
        self.assertEqual(instance.created_date, instance_copy.created_date)
        # pylint: disable=no-member
        self.assertIsNone(instance.created_date.tzinfo)
        self.assertIsNone(instance_copy.created_date.tzinfo)


class TestPayment(DatabaseFixture):
    def test_payment_big_value(self):
        value = 10000 * 10**18
        self.assertGreater(value, 2**64)
        payment = m_factory.TaskPayment(
            value=value,
        )
        payment.wallet_operation.save(force_insert=True)
        payment.save(force_insert=True)


class TestIncome(DatabaseFixture):
    def setUp(self):
        super().setUp()
        self.income = m_factory.Income()

    def test_status_overdue_but_settled(self):
        self.income.overdue = True
        self.income.value_received = self.income.value
        self.assertIs(self.income.status, m.PaymentStatus.confirmed)

    def test_status_overdue(self):
        self.income.overdue = True
        self.assertIs(self.income.status, m.PaymentStatus.overdue)

    def test_status_awaiting(self):
        self.assertIs(self.income.status, m.PaymentStatus.awaiting)


class TestLocalRank(DatabaseFixture):
    def test_default_fields(self):
        # pylint: disable=no-member
        r = m.LocalRank()
        self.assertGreaterEqual(datetime.now(), r.created_date)
        self.assertGreaterEqual(datetime.now(), r.modified_date)
        self.assertEqual(0, r.positive_computed)
        self.assertEqual(0, r.negative_computed)
        self.assertEqual(0, r.wrong_computed)
        self.assertEqual(0, r.positive_requested)
        self.assertEqual(0, r.negative_requested)
        self.assertEqual(0, r.positive_payment)
        self.assertEqual(0, r.negative_payment)
        self.assertEqual(0, r.positive_resource)
        self.assertEqual(0, r.negative_resource)
        self.assertEqual((0, 0, 0, 0), r.provider_efficacy.vector)


class TestGlobalRank(DatabaseFixture):
    def test_default_fields(self):
        r = m.GlobalRank()
        self.assertGreaterEqual(datetime.now(), r.created_date)
        self.assertGreaterEqual(datetime.now(), r.modified_date)
        self.assertEqual(m.NEUTRAL_TRUST, r.requesting_trust_value)
        self.assertEqual(m.NEUTRAL_TRUST, r.computing_trust_value)
        self.assertEqual(0, r.gossip_weight_computing)
        self.assertEqual(0, r.gossip_weight_requesting)


class TestNeighbourRank(DatabaseFixture):
    def test_default_fields(self):
        r = m.NeighbourLocRank()
        self.assertGreaterEqual(datetime.now(), r.created_date)
        self.assertGreaterEqual(datetime.now(), r.modified_date)
        self.assertEqual(m.NEUTRAL_TRUST, r.requesting_trust_value)
        self.assertEqual(m.NEUTRAL_TRUST, r.computing_trust_value)


class TestTaskPreset(DatabaseFixture):
    def test_default_fields(self):
        tp = m.TaskPreset()
        assert datetime.now() >= tp.created_date
        assert datetime.now() >= tp.modified_date


class TestPerformance(DatabaseFixture):
    def test_default_fields(self):
        perf = m.Performance()
        assert datetime.now() >= perf.created_date
        assert datetime.now() >= perf.modified_date
        assert perf.value == 0.0

    def test_constraints(self):
        perf = m.Performance()
        # environment_id can't be null
        with self.assertRaises(IntegrityError):
            perf.save()

        perf.environment_id = "ENV1"
        perf.save()

        perf = m.Performance(environment_id="ENV2", value=138.18)
        perf.save()

        env1 = m.Performance.get(m.Performance.environment_id == "ENV1")
        assert env1.value == 0.0
        env2 = m.Performance.get(m.Performance.environment_id == "ENV2")
        assert env2.value == 138.18

        # environment_id must be unique
        perf3 = m.Performance(environment_id="ENV1", value=1472.11)
        with self.assertRaises(IntegrityError):
            perf3.save()

        # value doesn't have to be unique
        perf3 = m.Performance(environment_id="ENV3", value=138.18)
        perf3.save()

    def test_update_or_create(self):
        m.Performance.update_or_create("ENVX", 100)
        env = m.Performance.get(m.Performance.environment_id == "ENVX")
        assert env.value == 100
        m.Performance.update_or_create("ENVX", 200)
        env = m.Performance.get(m.Performance.environment_id == "ENVX")
        assert env.value == 200
        m.Performance.update_or_create("ENVXXX", 300)
        env = m.Performance.get(m.Performance.environment_id == "ENVXXX")
        assert env.value == 300
        env = m.Performance.get(m.Performance.environment_id == "ENVX")
        assert env.value == 200
