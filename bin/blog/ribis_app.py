import os, re, html, subprocess

def genart(rootdir, dirpath, sitepath, config_path, env, post_data):
	art = ''
	blogpath = re.sub(r'/_ribis/config$|/_ribis/config/$', '', config_path)
	def posts(path, flist, limit):
		if 'index.md' in os.listdir(path) and os.path.isfile(os.path.join(path, 'index.md')):
			if len(flist) < limit:
				flist.append(os.path.join(path))
		else:
			if len(flist) < limit: 
				dirs = []
				for i in os.listdir(path):
					if os.path.isdir(os.path.join(path, i)) and re.match(r'[0-9]*$', i):
						dirs.append(i)
				dirs.sort()
				dirs.reverse()
				for i in dirs:
					posts(os.path.join(path, i), flist, limit)

	if os.path.exists(dirpath) and os.path.samefile(dirpath, blogpath):
		flist = []
		posts(dirpath, flist, 10)
		art += "\n<br><a href=\"post-list\">View all posts</a> &nbsp <a href=\"tags\">View all tags</a>"
		for i in flist:
			with open(os.path.join(i, 'index.md'), 'r') as post_fo:
				heading = post_fo.readline()
				postmd_full = post_fo.read()
			if heading[-1] == '\n':
				heading = heading[:-1]
			postmd = postmd_full[:600]
			heading = re.sub(r'^#*', '', heading)
			heading = re.sub(r' *$', '', heading)
			heading = f"<a href=\"/{html.escape(os.path.relpath(i, sitepath))}\">{html.escape(heading)}</a>"
			# if len(re.findall(r'(?<=/)[0-9]*?/[0-9]*?/[0-9]*?(?=/[0-9]*$|$)', i)) > 0:
			# 	heading += f"  ({re.findall(r'(?<=/)[0-9]*?/[0-9]*?/[0-9]*?(?=/[0-9]*$|$)', i)[0]})"
			heading = re.sub(r'^', '\n<br><br>\n<h1>', heading)
			heading += '</h1>'
			heading += f"\n<small><b><time>{re.sub(r'/', '-', os.path.relpath(i, dirpath))}</time> "
			postmd = re.sub(r'^( *?\n)|^\n', '', postmd)
			postmd = re.sub(r'(?<!\\)\{POSTDIR\}', '/' + os.path.relpath(i, sitepath), postmd)
			postmd_full = re.sub(r'^( *?\n)|^\n', '', postmd_full)
			postmd_full = re.sub(r'(?<!\\)\{POSTDIR\}', '/' + os.path.relpath(i, sitepath), postmd_full)
			if re.match(r'Tags:', postmd):
				tags = [j for j in re.findall(r'(?<=#)[a-z0-9\-]*', postmd.split('\n', 1)[0])]
				postmd = postmd.split('\n', 1)[1]
				postmd_full = postmd_full.split('\n', 1)[1]
				for j in tags:
					heading += f" <a href=\"{'/' + os.path.relpath(dirpath, sitepath) + '/tags/' + j}\">{j}</a>"
			heading += "</b></small>"

			art += heading
			# proc = subprocess.Popen(['cmark', '--unsafe', os.path.join(i, 'index.md')], stdout=subprocess.PIPE)
			# art += re.sub(r'^.*?\n', '', proc.stdout.read().decode() + '\n')
			proc = subprocess.Popen(['cmark', '--unsafe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			tmp = ''
			for j in postmd[::-1]:
				if j != '\n':
					tmp += j
				else:
					tmp += '\n'
					break
			if len(tmp) > 300:
				tmp = ''
				for j in postmd[::-1]:
					tmp += j
					if re.match(r' \.', tmp[-2:]):
						break
				tmp = tmp[:-1]
			if len(tmp) > 300:
				tmp = ''
				for j in postmd[::-1]:
					tmp += j
					if re.match(r' [a-zA-Z0-9]', tmp[-2:]):
						break
				tmp = tmp[:-1]
			postmd = re.sub(re.escape(tmp[::-1])+r'$', '', postmd)
			if postmd.strip() != postmd_full.strip():
				postmd += f" [Read more...]({os.path.relpath(i, dirpath)})"
			tmp = proc.communicate(input=postmd.encode())[0].decode()
			art += tmp

		http_status = '200 OK'
		http_headers = [('Content-Type', 'text/html')]

	elif re.match(r'.*/post-list$', dirpath) and os.path.samefile(blogpath, os.path.split(dirpath)[0]):
		art += '\n<h1>Posts</h1>'
		flist = []
		posts(blogpath, flist, 300)
		art += '\n<ul>'
		for i in flist:
			with open(os.path.join(i, 'index.md'), 'r') as post_fo:
				heading = post_fo.readline()
			if heading[-1] == '\n':
				heading = heading[:-1]
			heading = re.sub(r'^#*', '', heading)
			heading = re.sub(r' *$', '', heading)
			heading = f"\n<li><b><time>{re.sub(r'/', '-', os.path.relpath(i, blogpath))}</time></b> <a href=\"/{html.escape(os.path.relpath(i, sitepath))}\">{html.escape(heading)}</a></li>"
			art += heading
		art += '\n</ul>'

		http_status = '200 OK'
		http_headers = [('Content-Type', 'text/html')]

	elif re.match(r'.*/tags$', dirpath) and os.path.samefile(blogpath, os.path.split(dirpath)[0]):
		art += '\n<h1>Tags</h1>'
		tags = set()
		flist = []
		posts(blogpath, flist, 300)
		art += '\n<ul>'
		for i in flist:
			with open(os.path.join(i, 'index.md'), 'r') as post_fo:
				post_fo.readline()
				postmd = post_fo.read(100)
			postmd = re.sub(r'^( *?\n)|^\n', '', postmd)
			if re.match(r'Tags:', postmd):
				tags = set.union(tags, set([j for j in re.findall(r'(?<=#)[a-z0-9\-]*', postmd.split('\n', 1)[0])]))
		for i in tags:
			art += f"\n<li><tt><a href=\"{'/' + os.path.relpath(dirpath, sitepath) + '/' + i}\">{i}</a></tt></li>"
		art += '\n</ul>'

		http_status = '200 OK'
		http_headers = [('Content-Type', 'text/html')]

	elif re.match(r'.*/tags/[a-z0-9\-]*$', dirpath) and os.path.samefile(blogpath, os.path.split(os.path.split(dirpath)[0])[0]):
		tag = re.findall(r'(?<=/tags/)[a-z0-9\-]*$', dirpath)[0]
		plist = []
		flist = []
		posts(blogpath, flist, 300)
		for i in flist:
			with open(os.path.join(i, 'index.md'), 'r') as post_fo:
				post_fo.readline()
				postmd = post_fo.read(100)
				postmd = re.sub(r'^( *?\n)|^\n', '', postmd)
				if re.match(r'Tags:', postmd):
					if tag in [j for j in re.findall(r'(?<=#)[a-z0-9\-]*', postmd.split('\n', 1)[0])]:
						plist.append(i)
		art += f"\n<h1>Posts tagged <a href=\"{'/' + os.path.relpath(dirpath, sitepath)}\">#{tag}</a></h1>"
		art += '\n<ul>'
		for i in plist:
			with open(os.path.join(i, 'index.md'), 'r') as post_fo:
				heading = post_fo.readline()
			if heading[-1] == '\n':
				heading = heading[:-1]
			heading = re.sub(r'^#*', '', heading)
			heading = re.sub(r' *$', '', heading)
			art += f"\n<li><b><time>{re.sub(r'/', '-', os.path.relpath(i, blogpath))}</time></b> <a href=\"/{html.escape(os.path.relpath(i, sitepath))}\">{html.escape(heading)}</a></li>"
		art += '\n</ul>'
		http_status = '200 OK'
		http_headers = [('Content-Type', 'text/html')]

	else:
		if os.path.isfile(os.path.join(dirpath, '_header.md')):
			proc = subprocess.Popen(['cmark', '--unsafe', os.path.join(dirpath, '_header.md')], stdout=subprocess.PIPE)
			art += proc.stdout.read().decode() + '\n'
		if os.path.isfile(os.path.join(dirpath, 'index.md')):
			# proc = subprocess.Popen(['cmark', '--unsafe', os.path.join(dirpath, 'index.md')], stdout=subprocess.PIPE)
			# art += proc.stdout.read().decode()
			i = dirpath
			with open(os.path.join(i, 'index.md'), 'r') as post_fo:
				heading = post_fo.readline()
				postmd_full = post_fo.read()
			if heading[-1] == '\n':
				heading = heading[:-1]
			postmd = postmd_full[:600]
			heading = re.sub(r'^#*', '', heading)
			heading = re.sub(r' *$', '', heading)
			heading = f"\n<h1>{html.escape(heading)}</h1>"
			heading += f"\n<small><b><time>{re.sub(r'/', '-', os.path.relpath(i, blogpath))}</time> "
			postmd_full = re.sub(r'^( *?\n)|^\n', '', postmd_full)
			postmd_full = re.sub(r'(?<!\\)\{POSTDIR\}', '/' + os.path.relpath(i, sitepath), postmd_full)
			if re.match(r'Tags:', postmd_full):
				tags = [j for j in re.findall(r'(?<=#)[a-z0-9\-]*', postmd_full.split('\n', 1)[0])]
				postmd_full = postmd_full.split('\n', 1)[1]
				if tags != []:
					for j in tags:
						heading += f" <a href=\"{'/' + os.path.relpath(blogpath, sitepath) + '/tags/' + j}\">{j}</a>"
			heading += "</b></small>"
			art += heading	
			proc = subprocess.Popen(['cmark', '--unsafe'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			tmp = proc.communicate(input=postmd_full.encode())[0].decode()
			art += tmp

			http_status = '200 OK'
			http_headers = [('Content-Type', 'text/html')]


		elif os.path.isdir(dirpath):
			art += f"\n<h1 class=\"dir-list-head\"> {'/ ' + re.sub(r'/', ' / ', os.path.relpath(dirpath, sitepath))} </h1>"
			art += "\n<ul class=\"dir-list\">"
			flist = os.listdir(dirpath)
			flist.sort()
			dirlist = next(os.walk(dirpath))[1]
			dirlist.sort()
			for i in range(0, len(flist)):
				if flist[i] in dirlist:
					flist[i] += '/'
			for i in flist:
				if i != '_ribis/' and i != '_header.md' and i != '_footer.md':
					art += f"\n<li><a href=\"{'/' + os.path.relpath(os.path.join(dirpath, i), sitepath) + '/'}\">{i}</a></li>"
			art += "\n</ul>"

			http_status = '200 OK'
			http_headers = [('Content-Type', 'text/html')]

		else:
			with open(os.path.join(rootdir, 'tpl', '404.tpl'), 'r') as tpl_404:
				tmp = tpl_404.read()
			tmp = re.sub(r'(?<!\\)\{URL\}', env['HTTP_HOST']+env['REQUEST_URI'], tmp)
			art += tmp

			http_status = '404 Not Found'
			http_headers = [('Content-Type', 'text/html')]

		if os.path.isfile(os.path.join(dirpath, '_footer.md')):
			proc = subprocess.Popen(['cmark', '--unsafe', os.path.join(dirpath, '_footer.md')], stdout=subprocess.PIPE)
			art += proc.stdout.read().decode() + '\n'



	return (art, http_status, http_headers)
