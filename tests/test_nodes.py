"""Tests for expression tree node types."""

import dataclasses
from decimal import Decimal

import pytest

from quantum_money.nodes import Add, Div, Mul, Pow, Root, Round, Sub, Value


def test_value_node_stores_amount():
    node = Value(Decimal("10.33"))
    assert node.amount == Decimal("10.33")


def test_value_node_is_frozen():
    node = Value(Decimal("10"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        node.amount = Decimal("20")  # type: ignore[misc]


def test_value_nodes_with_same_amount_are_equal():
    assert Value(Decimal("10")) == Value(Decimal("10"))


def test_value_nodes_with_different_amounts_are_not_equal():
    assert Value(Decimal("10")) != Value(Decimal("20"))


def test_add_node_stores_children():
    left = Value(Decimal("5"))
    right = Value(Decimal("3"))
    node = Add(left, right)
    assert node.left == left
    assert node.right == right


def test_sub_node_stores_children():
    left = Value(Decimal("10"))
    right = Value(Decimal("3"))
    node = Sub(left, right)
    assert node.left == left
    assert node.right == right


def test_mul_node_stores_node_and_factor():
    inner = Value(Decimal("5"))
    node = Mul(inner, Decimal("3"))
    assert node.node == inner
    assert node.factor == Decimal("3")


def test_div_node_stores_node_and_divisor():
    inner = Value(Decimal("10"))
    node = Div(inner, Decimal("2"))
    assert node.node == inner
    assert node.divisor == Decimal("2")


def test_pow_node_stores_node_and_exponent():
    inner = Value(Decimal("4"))
    node = Pow(inner, Decimal("2"))
    assert node.node == inner
    assert node.exponent == Decimal("2")


def test_root_node_stores_node_and_index():
    inner = Value(Decimal("9"))
    node = Root(inner, Decimal("2"))
    assert node.node == inner
    assert node.index == Decimal("2")


def test_round_node_stores_node_rounding_and_places():
    inner = Value(Decimal("10.335"))
    node = Round(inner, "ROUND_HALF_UP", 2)
    assert node.node == inner
    assert node.rounding == "ROUND_HALF_UP"
    assert node.places == 2


@pytest.mark.parametrize(
    "node_a, node_b",
    [
        (
            Add(Value(Decimal("1")), Value(Decimal("2"))),
            Add(Value(Decimal("1")), Value(Decimal("2"))),
        ),
        (
            Mul(Value(Decimal("5")), Decimal("3")),
            Mul(Value(Decimal("5")), Decimal("3")),
        ),
        (
            Round(Value(Decimal("1.5")), "ROUND_HALF_UP", 0),
            Round(Value(Decimal("1.5")), "ROUND_HALF_UP", 0),
        ),
    ],
    ids=["add", "mul", "round"],
)
def test_identical_nodes_are_equal(node_a, node_b):
    assert node_a == node_b


def test_nested_tree_equality():
    tree_a = Add(Mul(Value(Decimal("10")), Decimal("3")), Value(Decimal("5")))
    tree_b = Add(Mul(Value(Decimal("10")), Decimal("3")), Value(Decimal("5")))
    assert tree_a == tree_b


def test_frozen_nodes_are_hashable():
    node = Value(Decimal("10"))
    assert hash(node) == hash(Value(Decimal("10")))
    node_set = {node, Value(Decimal("10"))}
    assert len(node_set) == 1
