#!/bin/bash
pandoc --from=markdown --to=rst README.md -o README.rst

echo "Remember to remove relative links.. (long_desc invalidated on pypi)"
