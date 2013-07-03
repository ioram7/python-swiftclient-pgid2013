#!/bin/sh
curl -X POST -d '{"realm": {"description": "Facebook IdP", "type": "idp.oauth", "id": "7c3a3df54c9f42f4aa5a742f369fde01", "links": {"self": "http://localhost:5000/v3/services/7c3a3df54c9f42f4aa5a742f369fde01"}, "name": "Facebook"}}' -H "X-Authentication-Type: federated" -H "Content-Type: application/json" http://openstack.bsbbs.com.br:5000/v2.0/

