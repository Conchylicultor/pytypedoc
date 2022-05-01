"""Tests for chain_dict."""


def test_chain_dict():

  cli_dict = ConfigDict()

  ChainDict(
      cli_dict,
      hp_dict,
  )
