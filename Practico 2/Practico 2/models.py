from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db= SQLAlchemy(app)

class Preceptor(db.Model):
    __tablename__ ='preceptor'
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(80), nullable=False)
    apellido=db.Column(db.String(80), nullable=False)
    correo=db.Column(db.String(120), unique=True, nullable=False)
    clave=db.Column(db.String(120), nullable=False)
    cursos = db.relationship("Curso", backref="preceptor", cascade="all, delete-orphan")


class Padre(db.Model):
    __tablename__ ='padre'
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(80), nullable=False)
    apellido=db.Column(db.String(80), nullable=False)
    correo=db.Column(db.String(120), unique=True, nullable=False)
    clave=db.Column(db.String(120), nullable=False)
    hijos = db.relationship('Estudiante', backref='padre', cascade="all, delete-orphan")

class Estudiante(db.Model):
    __tablename__ ='estudiante'
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(80), nullable=False)
    apellido=db.Column(db.String(80), nullable=False)
    dni=db.Column(db.String(10), nullable=False)
    idcurso=db.Column(db.Integer, db.ForeignKey('curso.id'))
    idpadre=db.Column(db.Integer, db.ForeignKey('padre.id'))
    asistencias = db.relationship('Asistencia', backref='estudiante', cascade="all, delete-orphan")


class Curso(db.Model):
    __tablename__ ='curso'
    id=db.Column(db.Integer, primary_key=True)
    anio=db.Column(db.String(80), nullable=False)
    division=db.Column(db.String(80), nullable=False)
    idpreceptor=db.Column(db.Integer, db.ForeignKey('preceptor.id'))
    estudiantes = db.relationship('Estudiante', backref='curso', cascade="all, delete-orphan")


class Asistencia(db.Model):
    __tablename__ ='asistencia'
    id=db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    codigoclase=db.Column(db.Integer, db.ForeignKey('curso.id'))
    asistio= db.Column(db.Text)
    justificacion=db.Column(db.String(100))
    idestudiante=db.Column(db.Integer, db.ForeignKey('estudiante.id'))
