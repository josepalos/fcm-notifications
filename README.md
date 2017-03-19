TODOs
=====
- [ ] Implement exponential back-off if an error from the server is received and the header contains
retry later or the topics message rate is exceeded.
- [ ] Decide the action to take when an error from the server is received but there is no retry later
header
- [x] Implement wrapper

Testing
=======
For running the tests run **python -m unittest discover**.