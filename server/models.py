from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

##~~~~~~~Scientist MODEL~~~~~~~~##
class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True) #CONSTRAINT: must have a name and the name must be unique (nullable=False, unique=True)
    field_of_study = db.Column(db.String, nullable=False) #CONSTRAINT: must have a field_of_study
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

##relationships: A Scientist has many Missions
    missions = db.relationship('Mission', back_populates='scientist')

##associations: A Scientist has many Planets through Missions
    planets = association_proxy('missions', 'planet')

##Serializer
    serialize_rules=('-missions.scientist', '-created_at', '-updated_at',)

##VALIDATIONS: must have a unique name, and a field_of_study (key is required)
    @validates('name')
    def validate_name(self, key, name):
        if len(name) < 1:
            raise ValueError('Scientist name must be longer than 1 letter')
        return name 
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if len(field_of_study) < 1:
            raise ValueError('Scientist field_of_study must be greater than 1 letter')
        return field_of_study

###start with Mission because it is the center of the relationships - the intermediary ###
##~~~~~~~~Mission MODEL~~~~~~~~##
class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False) #CONSTRAINT: Mission must have a name (nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False) #CONSTRAINT: Mission must have a scientist_id (nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False) #CONSTRAINT: Mission must have a planet_id (nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

##relationships: A Mission belongs to a Scientist and belongs to a Planet
    scientist = db.relationship('Scientist', back_populates='missions') 
    planet = db.relationship('Planet', back_populates='missions')

##serializer: prevent the data from repeating itself. Find the things that are going to come back to where you are (ex: look at the 'planet' relationship within Mission - back_populates='missions' aka '-planet.missions')
    serialize_rules= ('-planet.missions', '-scientist.missions',)

#VALIDATIONS: Mission must have a name, a scientist_id and a planet_id
    @validates('name')
    def validate_name(self, key, name):
        if len(name) < 1:
            raise ValueError('Mission name must be longer than 1 letter')
        return name 
    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        if not scientist_id:
            raise ValueError('Mission must have scientist')
        return scientist_id
    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        if not planet_id:
            raise ValueError('Mission must have planet')
        return planet_id

##~~~~~~Planet MODEL~~~~##  
class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

##relationships: A Planet has many Missions
    missions = db.relationship('Mission', back_populates='planet') #'planet' is singular on the mission table

##associations: A Planet has many Scientists through Missions
    scientists = association_proxy('missions', 'scientist') #'scientist' is singular inside Mission through the relationship 'missions'

##Serializer: look at relationship 'missions = db.relationship('Mission', back_populates='planet')'
#in the GET / planets route it tells us it just wants to see id, name, distance_from_earth, iamge, and nearest_star
    serialize_only=(
        "id",
        "name",
        "distance_from_earth",
        "nearest_star",
        "image",
    )


# add any models you may need. 