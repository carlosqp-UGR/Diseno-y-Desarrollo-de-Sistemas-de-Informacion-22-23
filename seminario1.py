# Grupo A3 (MCL). Integrantes:
# 	- Carlos Quesada Pérez
# 	- Jorge Lombardo Bergillos
# 	- Mario Piña Munera
# 	- Luis Manzano Arroyo
# 	- Davide D’Aloisio

import sys		# sys.exit()
import string	# generar cadena aleatoria
import random	# generar cadena aleatoria

import pyodbc #Libreria ODBC para conexion con BD

# funcion para generar un codigo de pedido aleatorio distinto para cada pedido nuevo
def generateCpedido():
	codpedido = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
	print('Generando codigo de pedido:' + codpedido)
	return codpedido

# programa principal
def main ():
	print ("DDSI SEMINARIO 1: ACCESO A BD")
	# el usuario inicia sesion
	usrname = input("Inicie sesion con su direccion de correo:  ")
	print("Sesion iniciada correctamente: ", usrname)

	conn = None
	cursor = None 

	# Comprobamos los drivers del cliente
	print("Comprobando los drivers de su equipo:", pyodbc.drivers())
	if len(pyodbc.drivers())==0:
		print("No tiene ningún driver instalado. Cancelando el programa...")
		sys.exit()	
	
	# Descargar driver para conexion a la BD
	# https://www.devart.com/odbc/oracle/download.html

	# Script de conexion
	# https://docs.devart.com/odbc/oracle/python.htm

	# Iniciamos una conexion con la BD
	driver = 'Devart ODBC Driver for Oracle'
	server = 'oracle0.ugr.es,1521' 
	database = 'practbd.oracle0.ugr.es' 
	uid = 'x7170495' 
	password = 'x7170495'
	conn = None
	cursor = None
		
	try:	
		connection_str = 'DRIVER={'+driver+'};Direct=True;Host='+server+';Service Name='+database+';User ID='+uid+';Password='+password
		conn = pyodbc.connect(connection_str)
		# creamos el cursor de conexion, nos permitirá realizar consultas y operaciones
		cursor = conn.cursor()
		
	except pyodbc.Error:
		print ("Error al establecer la conexion con la BD")
		sys.exit()

	# Antres de entrar al menu, realizamos un commit por si acaso, para tener el estado
	# inicial de la BD antes de realizar ninguna operación
	conn.commit()

	# mostramos el menu
	exit = False 	# true para salir del menu y finalizar el programa 
	while (not exit):
		print ( 'MENU PRINCIPAL\
		\n\t1: Borrar y crear nuevamente las tablas\
		\n\t2: Dar de alta nuevo pedido\
		\n\t3: Mostrar contenido de las tablas\
		\n\t4: Cerrar conexion y salir' )
				
		choice1 = int(input("Seleccione la opcion:\t"))
		
		if choice1==1:
			print ( '\t1: Borrar y crear nuevamente las tablas')
			
			# eliminamos todas las tablas y su contenido
			print ("Borrando tablas...")
			
			# importante el orden de borrado, detalle_pedido primero porque depende de las otras dos
			try:
				cursor.execute ("DROP TABLE detalle_pedido")
				print("Tabla 'detalle_pedido' borrada correctamente.")
			except pyodbc.Error:
				print ("Error al borrar, la tabla 'detalle_pedido' no existe aún.")

			try:
				cursor.execute ("DROP TABLE stock")
				print("Tabla 'stock' borrada correctamente.")
			except:
				print("Error al borrar, la tabla 'stock' no existe aún.")

			try:
				cursor.execute ("DROP TABLE pedido")
				print("Tabla 'pedido' borrada correctamente.")
			except:
				print("Error al borrar, la tabla 'pedido' no existe aún.")
			
			# guardamos los cambios
			conn.commit()
			
			print ("Tablas borradas con éxito")
			
			# creamos la tabla de stock
			print ("Creando tabla de stock y añadiendo valores por defecto...")

			cursor.execute ( "CREATE TABLE stock (\
								nombre VARCHAR(30) DEFAULT('XXXX'),\
								cproducto  CHAR(3) PRIMARY KEY,\
								cantidad INTEGER)" )
			
			# matriz de datos por defecto
			stock_data = [	['PlayStation 1', 'S01', 25],
							['PlayStation 2', 'S02', 30],
							['PlayStation 3', 'S03', 40],
							['PlayStation 4', 'S04', 15],
							['PlayStation 5', 'S05', 5],
							['PlayStation Portable (PSP)', 'S06', 70],
							['PlayStation VITA (PS-VITA)', 'S07', 10],
							['PlayStation 4 Pro', 'S08', 100],
							['PlayStation 4 Slim', 'S09', 80],
							['PlayStation 3 Slim', 'S10', 225]	]
							
			insert_query = '''INSERT INTO stock (nombre, cproducto, cantidad) VALUES (?, ?, ?);'''
			
			for row in stock_data:
				# definimos los valores a insertar
				values = (row[0], row[1], row[2]) 
				# insertamos los valores en la BD
				cursor.execute(insert_query, values)
				
			print ("Tabla 'stock' creada y rellenada correctamente")
			print ("Mostrando contenido de la tabla...")
			print ( '------------------Stock-----------------------')
			cursor.execute("SELECT * FROM stock")
			for row in cursor:
				print (row)
			
			# creamos la tabla de pedidos (vacia)
			print ("Creando tabla de pedidos...")
			
			cursor.execute ( "CREATE TABLE pedido (\
								cpedido CHAR(3) PRIMARY KEY,\
								ccliente  VARCHAR(30) NOT NULL,\
								fecha DATE)" )
								
			print ("Tabla 'pedido' creada correctamente")
			
			# creamos la tabla de detalle_pedido (vacia)
			print ("Creando tabla de detalle_pedido...")
			
			cursor.execute ( "CREATE TABLE detalle_pedido (\
								cpedido CHAR(3) REFERENCES pedido(cpedido),\
								cproducto CHAR(3)  REFERENCES stock(cproducto),\
								cantidad INTEGER,\
								PRIMARY KEY(cpedido, cproducto))" )
								
			print ("Tabla 'detalle_pedido' creada correctamente")
			
			# guardamos los cambios
			conn.commit()

		elif choice1==2:
			print("Creando un nuevo pedido...")
			# Generamos el codigo del nuevo pedido
			codpedido = generateCpedido()
			# Insertamos en tabla de pedidos
			cursor.execute("INSERT INTO pedido(cpedido, ccliente, fecha) VALUES ('"
			+ codpedido + "', '" + usrname + "', sysdate)")
			# Guardamos temporalmente con un savepoint
			cursor.execute("SAVEPOINT pedido_creado")
			# Informamos por pantalla
			print("Pedido creado (temporalmente)")

			# menu secundario
			exit2 = False
			while (not exit2):
				print (	'\t2: Dar de alta nuevo pedido\
						\n\t\t1: Añadir detalle de producto\
						\n\t\t2: Eliminar todos los detalles de producto\
						\n\t\t3: Cancelar pedido\
						\n\t\t4: Finalizar pedido' )

				choice2 = int(input("Seleccione la opcion:\t"))
				if choice2==1:
					print ('\t\t1: Añadir detalle de producto')
					# Mostramos la lista de productos disponibles
					print ('Seleccione el producto de entre los disponibles {nombre, codigo producto, cantidad}:')
					cursor.execute("SELECT * FROM stock")
					for row in cursor:
						print (row)
					# El cliente introduce el codigo del producto
					codpro = input("Introduzca el codigo del producto deseado:  ")
					# Buscamos si el producto introducido existe
					cursor.execute("SELECT * FROM stock WHERE cproducto='"+codpro+"'")
					# Guardamos la salida de la búsqueda en el string aux; si len(aux)==0, entonces no existe el producto
					aux = cursor.fetchall()	
					# print(aux)
					if (len(aux)==0):
						print('Lo sentimos, el producto seleccionado no existe')
					else:
						# El cliente introduce la cantidad deseada
						cantidad = int(float(input("Introduzca la cantidad ENTERA deseada: ")))
						# Buscamos si hay sufiente stock disponible
						cursor.execute("SELECT * FROM stock WHERE cproducto='"+codpro+"' AND cantidad>=" + str(cantidad) )
						aux = cursor.fetchall()
						# Si la busqueda es correcta y la cantidad es positiva
						if ((len(aux)>0) and cantidad>0):
							print("Actualizando tablas...")
							# Añadimos nuevo detalle de producto
							cursor.execute("INSERT INTO detalle_pedido(cpedido, cproducto, cantidad) VALUES ('" 
							+ codpedido + "', '" + codpro + "', " + str(cantidad) + ")" )
							print("Tabla detalle_pedido actualizada")
							# Actualizamos la tabla de stock, el atributo cantidad
							cursor.execute("UPDATE stock SET cantidad=(cantidad-"+str(cantidad)+") WHERE cproducto='"+codpro+"'")
							print("Tabla stock actualizada")
							# Al final del proceso, mostrar tablas...
							print ("Mostrando contenido de las tablas actualizadas...")
							print ( '------------------Stock-----------------------')
							cursor.execute("SELECT * FROM stock")
							for row in cursor:
								print (row)
							print ( '------------------Pedido----------------------')
							cursor.execute("SELECT * FROM pedido")
							for row in cursor:
								print (row)
							print ( '------------------Detalle_Pedido--------------')
							cursor.execute("SELECT * FROM detalle_pedido")
							for row in cursor:
								print (row)
						else:
							print("Cantidad inválida")

				elif choice2==2:
					print ('\t\t2: Eliminar todos los detalles de producto')
					print ("Eliminando todos los detalles de producto...")
					# Volvemos al savepoint inicial del menu secundario
					cursor.execute("ROLLBACK TO pedido_creado")
					# Al final del proceso, mostrar tablas...
					print ("Mostrando contenido de las tablas actualizadas...")
					print ( '------------------Stock-----------------------')
					cursor.execute("SELECT * FROM stock")
					for row in cursor:
						print (row)
					print ( '------------------Pedido----------------------')
					cursor.execute("SELECT * FROM pedido")
					for row in cursor:
						print (row)
					print ( '------------------Detalle_Pedido--------------')
					cursor.execute("SELECT * FROM detalle_pedido")
					for row in cursor:
						print (row) 
				
				elif choice2==3:
					print ('\t\t3: Cancelar pedido')
					# Para salir del menu secundario
					exit2 = True
					# Volvemos al último commit, no tiene el pedido creado
					cursor.execute("ROLLBACK")
					# Al final del proceso, mostrar tablas...
					print ("Mostrando contenido de las tablas actualizadas...")
					print ( '------------------Stock-----------------------')
					cursor.execute("SELECT * FROM stock")
					for row in cursor:
						print (row)
					print ( '------------------Pedido----------------------')
					cursor.execute("SELECT * FROM pedido")
					for row in cursor:
						print (row)
					print ( '------------------Detalle_Pedido--------------')
					cursor.execute("SELECT * FROM detalle_pedido")
					for row in cursor:
						print (row) 

				elif choice2==4:
					print ('\t\t4: Finalizar pedido')
					# Para salir del menu secundario
					exit2 = True
					print("Guardando cambios de forma permanente y finalizando pedido...")
					# Guardamos los cambio de forma permanente en la BD
					conn.commit()

				else:
					print ('Opcion invalida')
						
		elif choice1==3:
			print ( '\t3: Mostrar contenido de las tablas')
			print ( '------------------Stock-----------------------')
			try:
				cursor.execute("SELECT * FROM stock")
				for row in cursor:
					print (row)
			except pyodbc.Error:
				print ("Tabla 'stock' vacía")
			print ( '------------------Pedido----------------------')
			try:
				cursor.execute("SELECT * FROM pedido")
				for row in cursor:
					print (row)
			except pyodbc.Error:
				print ("Tabla 'pedido' vacía")
			print ( '------------------Detalle_Pedido--------------')
			try:
				cursor.execute("SELECT * FROM detalle_pedido")
				for row in cursor:
					print (row)
			except pyodbc.Error:
				print ("Tabla 'detalle_pedido' vacía")

		elif choice1==4:
			print (	'\t5: Cerrar conexion y salir')	
			exit = True
			
		else:
			print ('Opcion invalida')
		
	
	# cerrar conexion con la BD 
	print ("Cerrando Conexion con la BD...")
	cursor.close() 	# eliminamos el cursor
	conn.close() 	# cerramos la conexion
	print ("Conexion cerrada con éxito")
	
	# terminar el programa
	print("Finalizando programa...")
	
	return 0
	
# Ejecutamos el programa	
main()	