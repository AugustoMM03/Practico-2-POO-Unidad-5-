from flask import Flask, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')
app.config.from_pyfile('config.py')

from models import db
from models import Preceptor, Padre, Estudiante, Curso, Asistencia
from datetime import datetime
import hashlib

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/iniciar_sesion', methods = ['GET', 'POST'])
def iniciarSesion():
    if request.method == 'POST':
        email = request.form ['correo']
        clave = request.form['clave']
        tipoUsuario = request.form['tipoUsuario']

        if not email or not clave or not tipoUsuario:
            return render_template('error.html', error = "Error de inicio de sesion: faltan datos")

        if tipoUsuario == 'padre':
            usuario = Padre.query.filter_by(correo=email).first()
        elif tipoUsuario == 'preceptor':
            usuario = Preceptor.query.filter_by(correo=email).first()
        else:
            return render_template('error.html', error="Error de inicio de sesion")

        clavecifrada = hashlib.md5(clave.encode()).hexdigest()
        if usuario and usuario.clave == clavecifrada:
            if tipoUsuario == 'preceptor':
                session['id'] = usuario.id      # Guardar el valor de 'id' en session
                return render_template('sesionPreceptor.html')
            elif tipoUsuario == 'padre':
                return render_template('aviso.html', mensaje = "Se ha iniciado sesion correctamente")
                #return render_template('sesionPadre.py')
        else:
            #return render_template('error.html', error= f"Error de inicio de sesion: contraseña y/o correo incorrectos {usuario.clave} != {clavecifrada}")
            return render_template('error.html', error= f"Error de inicio de sesion: contraseña y/o correo incorrectos")
    
    return render_template('iniciarSesion.html')

@app.route('/registrar_asistencia', methods = ['GET', 'POST'])
def registrarAsistencia():
    
    if 'id' in session:
        idUsuario = session['id']
        sespreceptor = Preceptor.query.get(idUsuario)

        if request.method == 'POST':
            if 'curso' not in request.form:
                return render_template('registrarAsistencia.html', cursos=Curso.query.all(), curso_selecc=None, preceptor=sespreceptor)
            else:
                selcursoid  = int(request.form['curso'])
                curso_selecc = Curso.query.get(selcursoid)
                estudiantes = Estudiante.query.filter_by(idcurso=curso_selecc.id).order_by(Estudiante.apellido, Estudiante.nombre).all()
                render_template('registrarAsistencia.html', cursos=None, curso_selecc=curso_selecc, preceptor=sespreceptor, estudiantes=estudiantes)
                for estudiante in estudiantes:
                    selclase = request.form.get('clase', '')
                    selasis = request.form.get('asistencia', '')
                    seljustific = request.form.get('justificacion', '')
                    #selfecha = request.form.get('fecha', '')                
                    #selfecha = datetime.strptime(request.form.get('fecha', ''), '%Y-%m-%d')
                    selfecha = datetime.today()
                    asistencia = Asistencia(fecha=selfecha, codigoclase=selclase,asistio=selasis,justificacion=seljustific,idestudiante=estudiante.id)
                    db.session.add(asistencia)
                db.session.commit()
                return render_template('registrarAsistencia.html', cursos=None, curso_selecc=curso_selecc, preceptor=sespreceptor, estudiantes=estudiantes)
        else:
            return render_template('registrarAsistencia.html', cursos=Curso.query.all(), selcurso=None, preceptor=sespreceptor)
    else:
        return render_template('error.html', error='Debe iniciar sesión como preceptor para acceder a esta página.')
      



@app.route('/obtener_informe', methods=['GET', 'POST'])
def obtenerInforme():
    informe = []
    if 'id' in session:
        idUsuario = session['id']
        selpreceptor = Preceptor.query.get(idUsuario)
        if request.method == 'POST':
            if not request.form['curso']:
                return render_template('obtenerInforme.html', cursos=Curso.query.all(), curso_selecc=None, preceptor=selpreceptor)
            else:
                curso_id = request.form['curso']
                curso_selecc = Curso.query.get(curso_id)
                estudiantes = Estudiante.query.filter_by(idcurso=curso_selecc.id).order_by(Estudiante.apellido, Estudiante.nombre).all()
                for estudiante in estudiantes:
                    ctotal=0
                    asistencias = Asistencia.query.filter_by(idestudiante=estudiante.id).all()
                    clases_aula_presentes = sum(1 for asistencia in asistencias if asistencia.asistio=='s' and asistencia.codigoclase == 1)
                    clases_edu_fis_presentes = sum(1 for asistencia in asistencias if asistencia.asistio=='s' and asistencia.codigoclase == 2)
                    clases_aula_aus_justificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 1)    
                    clases_aula_aus_injustificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 1) 
                    clases_edu_aus_justificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 2)    
                    clases_edu_aus_injustificadas = sum(1 for asistencia in asistencias if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 2)  
                    for asistencia in asistencias:
                        if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 1:
                            ctotal+=1
                        if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 1:
                            ctotal+=1
                        if  asistencia.asistio=='n' and asistencia.justificacion!=None and asistencia.codigoclase == 2:
                            ctotal+=0.5
                        if  asistencia.asistio=='n' and asistencia.justificacion==None and asistencia.codigoclase == 2:
                            ctotal+=0.5
                        
                    estudiante_info = {
                    'apellido': estudiante.apellido,
                    'nombre': estudiante.nombre,
                    'clases_aula_presentes': clases_aula_presentes,
                    'clases_edu_fis_presentes': clases_edu_fis_presentes,
                    'clases_aula_aus_justificadas': clases_aula_aus_justificadas,
                    'clases_aula_aus_injustificadas':clases_aula_aus_injustificadas,
                    'clases_edu_aus_justificadas':clases_edu_aus_justificadas,
                    'clases_edu_aus_injustificadas':clases_edu_aus_injustificadas,
                    'total_de_inasistencias':ctotal
                    }

                    informe.append(estudiante_info)

                return render_template('obtenerInforme.html', cursos=None, curso_selecc=curso_selecc, preceptor=selpreceptor,informe=informe)
        else:
            return render_template('obtenerInforme.html', cursos=Curso.query.all(), curso_selecc=None, preceptor=selpreceptor)
    else:
        return render_template('error.html', error='Debe iniciar sesión como preceptor para acceder a esta página.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)