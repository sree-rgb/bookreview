# /usr/bin/python
def sigunupvaildr(username,pass1,pass2,email):

	if pass1 != pass2:
		return ('Enter Same password',1)
	if pass1.isspace() or pass1.isnumeric():
		return ('Enter valid password',1)
	if not username.isalnum():
		return ('Username should be contain letters and numbers',1)
	return ('Passed',0)