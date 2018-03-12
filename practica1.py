#!/usr/bin/python3

import webapp
import csv
import urllib
import urllib.parse

class reduceURLs(webapp.webApp):
	# Creo los diccionarios que vamos a usar.
	diccionario_URLs_completas = {} # Guardamos aquí las URLs completas.
	diccionario_URLs_cortas = {} # Guardamos aquí las URLs cortas.

	try: # Abro el fichero database.csv para leer las URLs guardadas en el.
		with open('database.csv','a') as csvfile: # Si no existe dicho fichero lo creo con la terminación open ('fichero','a').
			leedatabase = csv.reader(csvfile) # Método para leer de fichero.
			for row in leedatabase:
				Url_corta = row[0]
				Url_completa = row[1]
				diccionario_URLs_completas[Url_completa] = Url_corta # En este diccionario esta la key Url_completa y el value de Url_corta.
				diccionario_URLs_cortas[Url_corta] = Url_completa # En este diccionario esta la key Url_corta y el value de Url_completa.

	except:	# Una vez que he creado el fichero lo dejo cerrado.
		csvfile.close()

####### RECIBO LA PETICIÓN Y EXTRAIGO LA INFORMACIÓN ########

	def parse(self, request):
		# Nos quedamos con el método ya sea GET, PUT o POST de la solicitud.
		method = request.split(' ',2)[0]

		try: # Nos quedamos con el recurso que viene detrás de localhost:1234/.
			resource = request.split(' ',2)[1]
		except: # Por defecto introduciremos / al final que nos lleva al formulario.
			resource = "/"

		try: # Nos quedamos con el body de la solicitud recibida.
			request = request.split('\r\n\r\n')[1]
		except IndexError: # Por defecto introduciremos "".
			request = ""

		return(method, resource, request)

####### PROCESO LA PETICIÓN Y DEVUELVO EN CONSECUENCIA ########

	def process(self, filtered_request):
		method, resource, request = filtered_request
		if method == "GET":	# Si el método es GET:
			if (resource != '/'): # Si no se solicita nada devolvemos el formulario y la lista de las urls guardadas en database.
				Url_search = 'http://localhost:1234' + str(resource)
				try:
					Url_database = self.diccionario_URLs_cortas[Url_search]
					httpCode = "200 OK"
					htmlBody = '<html><head><meta http-equiv="Refresh" content="5;url='+ Url_database +'"></head>' \
						+ "<body><h1><p style='color:blue;'>Redirigiendo en 5 segundos...</p>" + "<img src='https://blog.hostalia.com/wp-content/themes/hostalia/images/redirigir-dominio-blog-hostalia-hosting.jpg'>" \
						+ "</h1></body></html>"
				except KeyError: # Si no introducimos correctamente el request, indicamos como hacerlo correctamente.
					httpCode = "200 OK"
					htmlBody = "<html><body>" \
					+ ' HTTP ERROR: Recurso no disponible.<br>' \
					+ ' Pruebe con localhost:1234/' \
					+ "</body></html>"

			else: # Si solicitan algo será la Url_completa que lleva asociado la Url_corta.
				httpCode = "200 OK"
				htmlBody = "<html><body>"  \
					+ '<form method="POST" action="">' \
					+ 'URL a acortar: <input type="text" name="url"><br>' \
					+ '<input type="submit" value="Enviar"><br>' \
					+ '</form>' \
					+ "</body></html>"

				for key, value in self.diccionario_URLs_completas.items():
					htmlBody = htmlBody + '<html><body><a href="'+ key +'">' + key + ' </a></br></body></html>' \
					+ '<html><body><a href="'+ value +'">'+ value + ' </a></br></body></html>'

		# Si el método que nos llega es PUT o POST envío el formulario.
		elif method == "PUT" or method == "POST":
			if request.split("=")[1] != "": # Comprobamos que el body no esta vacío.
				Url_nueva = request.split("=")[1]
				Url_nueva = urllib.parse.unquote(Url_nueva, encoding='utf-8', errors='replace')	# Lo paso en un string en utf-8.

				# Si no introducen la URL con el encabezamiento http lo añadimos nosotros.
				http = str(Url_nueva.split("://")[0])
				if (http != 'http') and (http != 'https'):
					Url_nueva = 'http://' + Url_nueva

				try:
					Url_corta = self.diccionario_URLs_completas[Url_nueva] # Si la url ya ha sido acortada la devuelvo.
					httpCode = "200 OK"
					htmlBody = "<html><body><h1> Esta URL ya ha sido corta " \
					+ "</h1></body></html>" \
					+ "\r\n" \
					+'<html><body>URL completa: <a href="'+ Url_nueva +'">' + Url_nueva + ' </a></br></body></html>'\
					+ '<html><body>URL corta: <a href="'+ Url_corta +'">'+ Url_corta + ' </a></br></body></html>'

				except KeyError: # Si no ha sido acortada la creo de nuevo.
					contador = len(self.diccionario_URLs_completas)	# Asigno el siguiente valor disponible en el diccionario.
					Url_corta_nueva = 'http://localhost:1234/' + str(contador)
					self.diccionario_URLs_completas[Url_nueva] = Url_corta_nueva
					self.diccionario_URLs_cortas[Url_corta_nueva] = Url_nueva
					with open ('database.csv', 'a') as csvfile:
						introducir_nueva = csv.writer(csvfile)
						introducir_nueva.writerow([Url_corta_nueva,Url_nueva])
					httpCode = "200 OK"
					htmlBody = "<html><body>Se ha acortado la URL de forma correcta</br>" \
					+'URL completa: <a href="'+ Url_nueva +'">' + Url_nueva + ' </a></br>'\
					+'URL corta: <a href="'+ Url_corta_nueva +'">'+ Url_corta_nueva + '</a></br></body></html>'

			else: # Si el body esta vacío, avisamos del error.
				httpCode = "200 OK"
				htmlBody = "<html><body>" \
				+ 'ERROR:  URL NO VALIDA.' \
				+ "</body></html>"

		else: # Si no recibimos un GET, un PUT o un POST, avisamos del error.
			httpCode = "450 MÉTODO NO VALIDO"
			htmlBody = "El método introducido no valido"
		return (httpCode, htmlBody)


if __name__ == "__main__":
	myWebApp = reduceURLs("localhost", 1234)
