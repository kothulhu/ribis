import re, html, os, subprocess, mimetypes, urllib

def application(env, start_response):

	rootdir = '/home/rishab/src/ribis' 

	sitepath = os.path.join(rootdir, 'sites', re.sub(r':[0-9]*$', '', env['HTTP_HOST']))
	dirpath = os.path.join(sitepath, re.sub(r'^/', '', env['REQUEST_URI']))

	if '..' in os.path.relpath(dirpath, sitepath):
		dirpath = sitepath
	if dirpath[-1:] == '/':
		dirpath = dirpath[:-1]

	def findrf(dirpath, rootdir, fname):
		found = False
		while os.path.relpath(dirpath, os.path.join(rootdir, 'sites')) != '.' and found == False:
			if os.path.isfile(os.path.join(dirpath, fname)):
				found = True
				return os.path.join(dirpath, fname)
			else:
				dirpath = os.path.split(dirpath)[0]
	
	
	def navbar(dirpath, sitepath, tmp_sitepath, ltxt):
		if os.path.exists(dirpath):
			relpath = os.path.relpath(dirpath, tmp_sitepath) + '/'
		else:
			tmp_dirpath = dirpath
			while not os.path.exists(tmp_dirpath) and sitepath in tmp_dirpath:
				tmp_dirpath = os.path.split(tmp_dirpath)[0]
			relpath = os.path.relpath(tmp_dirpath, tmp_sitepath) + '/'
		tmp_alldirs = next(os.walk(tmp_sitepath))[1]
		alldirs = []
		for i in range(0, len(tmp_alldirs)):
			if not '_ribis' in tmp_alldirs[i] and tmp_alldirs[i][0] != '.':
				alldirs.append(tmp_alldirs[i] + '/')
		if alldirs != []:
			ltxt.append('\n<ul>')
			alldirs.sort()
			tmp = os.path.relpath(tmp_sitepath, sitepath)
			if tmp == '.':
				tmp = '/'
			else:
				tmp = '/' + tmp + '/'
			for i in alldirs:
				if re.findall(r'^.*?/', relpath)[0] != i:
					ltxt.append(f"\n<li><a href=\"{tmp + i}\">&rsaquo; {re.sub(r'(?<=.)-(?=.)', ' ', i.title())[:-1]} </a></li>")
				else:
					ltxt.append(f"\n<li><a href=\"{tmp + i}\"><i> &raquo; {re.sub(r'(?<=.)-(?=.)', ' ', i.title())[:-1]} </i></a></li>")
					navbar(dirpath, sitepath, os.path.join(tmp_sitepath, i), ltxt)
			ltxt.append('\n</ul>')
		tmp = ''
		for i in ltxt:
			tmp += i
		return tmp


	def genhtm(rootdir, dirpath, sitepath, post_data):
		htm = ''
		with open(os.path.join(rootdir, 'tpl', 'head.tpl'), 'r') as head_fo:
			tmp = head_fo.read()
			if os.path.relpath(dirpath, sitepath) == '.':
				tmp = re.sub(r'\{TITLE\}', re.findall(r'.*?(?=:.*$)', env['HTTP_HOST'])[0], tmp)
			else:
				tmp = re.sub(r'\{TITLE\}', re.sub(r'/', ' - ', re.sub(r'(?<=[a-zA-z])-(?=[a-zA-z])', ' ', os.path.relpath(dirpath, sitepath))), tmp)
			if findrf(dirpath, rootdir, os.path.join('_ribis', 'lib', 'style.css')):
				tmp = re.sub(r'\{STYLESHEET\}', '/' + os.path.relpath(findrf(dirpath, rootdir, os.path.join('_ribis', 'lib', 'style.css')), sitepath), tmp)
			elif os.path.isfile(os.path.join(sitepath, '_ribis', 'lib', 'style.css')):
				tmp = re.sub(r'\{STYLESHEET\}', '/_ribis/lib/style.css', tmp)
			else:
				tmp = re.sub(r'\{STYLESHEET\}', '', tmp)
			try:
				with open(findrf(dirpath, rootdir, os.path.join('_ribis', 'config')), 'r') as config_fo:
					if 'mathjax' in config_fo.read():
						with open(os.path.join(rootdir, 'lib', 'mathjax.inc'), 'r') as mathjax_fo:
							tmp = re.sub(r'(?<=\{SCRIPTS\})\n', '\n' + mathjax_fo.read() + '\n', tmp)
			except:
				pass
			tmp = re.sub(r'\{SCRIPTS\}', '', tmp)

		htm += tmp
		htm += '\n<body>'

		htm += '\n'
		if os.path.isfile(os.path.join(sitepath, '_ribis', 'inc', 'header.inc')):
			with open(os.path.join(sitepath, '_ribis', 'inc', 'header.inc'), 'r') as header_fo:
				htm += header_fo.read()
		else:
			with open(os.path.join(rootdir, 'tpl', 'header.tpl'), 'r') as header_fo:
				tmp = header_fo.read()
				try:
					with open(findrf(dirpath, rootdir, os.path.join('_ribis', 'config')), 'r') as config_fo:
						tmp2 = config_fo.read()
					if 'title=' in tmp2:
						tmp = re.sub(r'\{TITLE\}', re.findall(r'(?<=title\=).*(?=\n|$)', tmp2)[0], tmp)
					else:
						tmp = re.sub(r'\{TITLE\}', re.findall(r'.*?(?=:.*$)', env['HTTP_HOST'])[0], tmp)
					if 'subtitle=' in tmp2:
						tmp = re.sub(r'\{SUBTITLE\}', re.findall(r'(?<=subtitle\=).*(?=\n|$)', tmp2)[0], tmp)
					else:
						tmp = re.sub(r'\{SUBTITLE\}', 'my personal /var/www/dump', tmp)
				except:
					tmp = re.sub(r'\{TITLE\}', re.findall(r'.*?(?=:.*$)', env['HTTP_HOST'])[0], tmp)
					tmp = re.sub(r'\{SUBTITLE\}', 'my personal /var/www/dump', tmp)
				htm += tmp


		stxt = '\n<nav id="side-bar">'
		stxt += '\n<div>'

		ltxt = []
		stxt += navbar(dirpath, sitepath, sitepath, ltxt)
		stxt += '\n</div>'
		stxt += '\n</nav>'

		htm += stxt


		htm += '\n<article>'

		spec_art = ''

		htm += '\n'
		config_path = findrf(dirpath, rootdir, os.path.join('_ribis', 'config'))
		if dirpath != '' and config_path != None:
			with open(config_path, 'r') as config_fo:
				config = config_fo.read()
		else:
			config = ''

		if 'spec-art' in config:
			art_handler = os.path.join(rootdir, re.findall(r'(?<=spec-art:\{ROOTDIR\}/).*', config)[0])
			os.chdir(os.path.split(art_handler)[0])
			import ribis_app
			tmp = ribis_app.genart(rootdir, dirpath, sitepath, config_path, env, post_data)
			htm += tmp[0]
			http_status = tmp[1]
			http_headers = tmp[2]
		else:
			if os.path.isfile(os.path.join(dirpath, '_header.md')):
				proc = subprocess.Popen(['cmark', '--unsafe', os.path.join(dirpath, '_header.md')], stdout=subprocess.PIPE)
				htm += proc.stdout.read().decode() + '\n'
			if os.path.isfile(os.path.join(dirpath, 'index.md')):
				proc = subprocess.Popen(['cmark', '--unsafe', os.path.join(dirpath, 'index.md')], stdout=subprocess.PIPE)
				htm += proc.stdout.read().decode()

				http_status = '200 OK'
				http_headers = [('Content-Type', 'text/html')]

			elif os.path.isdir(dirpath):
				htm += f"\n<h1 class=\"dir-list-head\"> {'/ ' + re.sub(r'/', ' / ', os.path.relpath(dirpath, sitepath))} </h1>"
				htm += "\n<ul class=\"dir-list\">"
				flist = os.listdir(dirpath)
				flist.sort()
				dirlist = next(os.walk(dirpath))[1]
				dirlist.sort()
				for i in range(0, len(flist)):
					if flist[i] in dirlist:
						flist[i] += '/'
				for i in flist:
					if i != '_ribis/' and i != '_header.md' and i != '_footer.md':
						htm += f"\n<li><a href=\"{'/' + os.path.relpath(os.path.join(dirpath, i), sitepath) + '/'}\">{i}</a></li>"
				htm += "\n</ul>"

				http_status = '200 OK'
				http_headers = [('Content-Type', 'text/html')]

			else:
				with open(os.path.join(rootdir, 'tpl', '404.tpl'), 'r') as tpl_404:
					tmp = tpl_404.read()
				tmp = re.sub(r'(?<!\\)\{URL\}', env['HTTP_HOST']+env['REQUEST_URI'], tmp)
				htm += tmp

				http_status = '404 Not Found'
				http_headers = [('Content-Type', 'text/html')]

			if os.path.isfile(os.path.join(dirpath, '_footer.md')):
				proc = subprocess.Popen(['cmark', '--unsafe', os.path.join(dirpath, '_footer.md')], stdout=subprocess.PIPE)
				htm += proc.stdout.read().decode() + '\n'


		htm += '\n</article>'


		htm += '\n</body>'
		htm += '\n</html>'

		return (htm, http_status, http_headers)

	for i in env['wsgi.input']:
		post_data = i.decode()
	try:
		post_data
	except:
		post_data = ''

	if os.path.isdir(dirpath):
		tmp = genhtm(rootdir, dirpath, sitepath, post_data)
		start_response(tmp[1], tmp[2])
		return [tmp[0].encode()]
	elif os.path.isfile(dirpath) and dirpath[-3:] == '.md':
		start_response('200 OK', [('Content-Type', 'text/plain')])
		with open(dirpath, 'r') as ind_fo:
			return [ind_fo.read().encode()]
	elif os.path.isfile(dirpath):
		if mimetypes.guess_type(dirpath)[0] != None:
			start_response('200 OK', [('Content-Type', mimetypes.guess_type(dirpath)[0])])
		elif dirpath[-4:] == '.asc':
			start_response('200 OK', [('Content-Type', 'text/plain')])
		else:
			start_response('200 OK', [('Content-Type', 'application/octet-stream')])
		with open(dirpath, 'rb') as ind_fo:
			return [ind_fo.read()]
	else:
		tmp = genhtm(rootdir, dirpath, sitepath, post_data)
		start_response(tmp[1], tmp[2])
		return [tmp[0].encode()]
