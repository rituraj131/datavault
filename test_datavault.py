#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import socket
import threading
import unittest
import time

from datavault.datavault import DataVault


class TestDatavault(unittest.TestCase):
    """Tests for `datavault` package."""

    def setUp(self):
        self.vault = DataVault(port=0)
        self.server_thread = threading.Thread(target=self.vault.start)
        self.server_thread.start()
        time.sleep(1)
        self.port = self.vault.actual_port()

    def tearDown(self):
        self.vault.stop()
        self.server_thread.join(400)

    def test_t1(self):
        """Test if the server has started without errors."""
        client = self._get_client_sock()

        client.sendall("""
            as principal admin password "admin" do
               create principal bob "bob"
               create principal alice "alice"
               set x = "string"
               set delegation x admin write -> bob
               return "admin out"
            ***
        """)

        # receive the response data (4096 is recommended buffer size)
        response = client.recv(4096)
        print response

        print '--------- 2 ----------'
        client2 = self._get_client_sock()
        client2.sendall("""
            as principal bob password "bob" do
               set delegation x bob write -> alice
               return "this entire exec should be DENIED"
            ***
        """)

        # receive the response data (4096 is recommended buffer size)
        response = client2.recv(4096)
        print repr(response)

    def _get_client_sock(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', self.port))
        return client


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
