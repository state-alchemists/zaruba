from typing import List
from helper import cli
import helper.generator as generator

import os, re

route_template = '''

    # List {entity} route
    @app.get('/{entity}s/', response_model=List[schema.{entity_caption}])
    def crud_list_{entity}(skip: int = 0, limit: int = 100):
        try:
            db_{entity}_list = mb.call_rpc('list_{entity}', skip, limit)
            return [schema.{entity_caption}.parse_obj(db_{entity}) for db_{entity} in db_{entity}_list]
        except Exception:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail='Internal server error')


    # Get {entity} route
    @app.get('/{entity}s/{{{entity}_id}}', response_model=schema.{entity_caption})
    def crud_get_{entity}({entity}_id: int):
        try:
            db_{entity} = mb.call_rpc('get_{entity}', {entity}_id)
            if db_{entity} is None:
                raise HTTPException(status_code=404, detail='{entity_caption} not found')
            return schema.{entity_caption}.parse_obj(db_{entity})
        except Exception:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail='Internal server error')


    # Create {entity} route
    @app.post('/{entity}s/', response_model=schema.{entity_caption})
    def crud_create_{entity}({entity}_data: schema.{entity_caption}Create):
        try:
            db_{entity} = mb.call_rpc('create_{entity}', {entity}_data.dict())
            if db_{entity} is None:
                raise HTTPException(status_code=404, detail='{entity_caption} not created')
            return schema.{entity_caption}.parse_obj(db_{entity})
        except Exception:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail='Internal server error')


    # Update {entity} route
    @app.put('/{entity}s/{{{entity}_id}}', response_model=schema.{entity_caption})
    def crud_update_{entity}({entity}_id: int, {entity}_data: schema.{entity_caption}Update):
        try:
            db_{entity} = mb.call_rpc('update_{entity}', {entity}_id, {entity}_data.dict())
            if db_{entity} is None:
                raise HTTPException(status_code=404, detail='{entity_caption} not found')
            return schema.{entity_caption}.parse_obj(db_{entity})
        except Exception:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail='Internal server error')


    # Delete {entity} route
    @app.delete('/{entity}s/{{{entity}_id}}', response_model=schema.{entity_caption})
    def crud_get_{entity}({entity}_id: int):
        try:
            db_{entity} = mb.call_rpc('delete_{entity}', {entity}_id)
            if db_{entity} is None:
                raise HTTPException(status_code=404, detail='{entity_caption} not found')
            return schema.{entity_caption}.parse_obj(db_{entity})
        except Exception:
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail='Internal server error')

'''

event_template = '''

    # List {entity} message handler
    @transport.handle_rpc(mb, 'list_{entity}')
    @database.handle(DBSession)
    def crud_rpc_list_{entity}(db: Session, skip: int = 0, limit: int = 100) -> List[Mapping[str, Any]]:
        try:
            db_{entity}_list = crud.list_{entity}(db, skip = skip, limit = limit)
            return [schema.{entity_class}.from_orm(db_{entity}).dict() for db_{entity} in db_{entity}_list]
        except Exception:
            print(traceback.format_exc())
            raise


    # Get {entity} message handler
    @transport.handle_rpc(mb, 'get_{entity}')
    @database.handle(DBSession)
    def crud_rpc_get_{entity}(db: Session, {entity}_id: int) -> Mapping[str, Any]:
        try:
            db_{entity} = crud.get_{entity}(db, {entity}_id = {entity}_id)
            if db_{entity} is None:
                return None
            return schema.{entity_class}.from_orm(db_{entity}).dict()
        except Exception:
            print(traceback.format_exc())
            raise


    # Create {entity} message handler
    @transport.handle_rpc(mb, 'create_{entity}')
    @database.handle(DBSession)
    def crud_rpc_create_{entity}(db: Session, {entity}_dict: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            db_{entity} = crud.create_{entity}(db, {entity}_data = schema.{entity_class}Create.parse_obj({entity}_dict))
            if db_{entity} is None:
                return None
            return schema.{entity_class}.from_orm(db_{entity}).dict()
        except Exception:
            print(traceback.format_exc())
            raise


    # Update {entity} message handler
    @transport.handle_rpc(mb, 'update_{entity}')
    @database.handle(DBSession)
    def crud_rpc_update_{entity}(db: Session, {entity}_id: int, {entity}_dict: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            db_{entity} = crud.update_{entity}(db, {entity}_id = {entity}_id, {entity}_data = schema.{entity_class}Update.parse_obj({entity}_dict))
            if db_{entity} is None:
                return None
            return schema.{entity_class}.from_orm(db_{entity}).dict()
        except Exception:
            print(traceback.format_exc())
            raise


    # Delete {entity} message handler
    @transport.handle_rpc(mb, 'delete_{entity}')
    @database.handle(DBSession)
    def crud_rpc_delete_{entity}(db: Session, {entity}_id: int) -> Mapping[str, Any]:
        try:
            db_{entity} = crud.delete_{entity}(db, {entity}_id = {entity}_id)
            if db_{entity} is None:
                return None
            return schema.{entity_class}.from_orm(db_{entity}).dict()
        except Exception:
            print(traceback.format_exc())
            raise

'''

crud_template = '''

# List {entity}
def list_{entity}(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.{entity_class}).offset(skip).limit(limit).all()


# Get {entity}
def get_{entity}(db: Session, {entity}_id: int):
    return db.query(model.{entity_class}).filter(model.{entity_class}.id == {entity}_id).first()


# Create {entity}
def create_{entity}(db: Session, {entity}_data: schema.{entity_class}Create):
    db_{entity} = model.{entity_class}({init_property})
    if db_{entity} is None:
        raise Error('Cannot create {entity}')
    db.add(db_{entity})
    db.commit()
    db.refresh(db_{entity})
    return db_{entity}


# Update {entity}
def update_{entity}(db: Session, {entity}_id: int, {entity}_data: schema.{entity_class}Update):
    db_{entity} = get_{entity}(db, {entity}_id)
    if db_{entity} is None:
        return None
    {update_property}
    db.add(db_{entity})
    db.commit()
    db.refresh(db_{entity})
    return db_{entity}


# Delete {entity}
def delete_{entity}(db: Session, {entity}_id: int):
    db_{entity} = get_{entity}(db, {entity}_id)
    if db_{entity} is None:
        return None
    db.delete(db_{entity})
    db.commit()
    return db_{entity}

'''

model_template = '''

# {entity} model
class {entity_class}(Base):
    __tablename__ = '{entity}s'
    id = Column(Integer, primary_key=True, index=True)
    {model_field_declaration}

'''

schema_template = '''

# {entity} schema

class {entity_class}Base(BaseModel):
    {schema_field_declaration}

class {entity_class}Create({entity_class}Base):
    pass

class {entity_class}Update({entity_class}Base):
    pass

class {entity_class}({entity_class}Base):
    id: int
    class Config:
        orm_mode = True

'''

@cli
def create_fast_crud(location: str, module: str, entity: str, str_fields: str):
    fields = str_fields.split(',') if str_fields != '' else []
    # declare substitutions
    indentation = '    '
    indented_new_line = '\n' + indentation
    entity = re.sub(r'[^A-Za-z0-9_]+', '_', entity).lower()
    entity_class = entity.capitalize()
    entity_caption = entity.replace('_', ' ').capitalize()
    model_field_declaration = indented_new_line.join([
        '{field} = Column(String)'.format(field = field) 
        for field in fields 
    ])
    schema_field_declaration = 'pass'
    if len(fields) > 0:
        schema_field_declaration = indented_new_line.join([
            '{field} : str'.format(field = field) 
            for field in fields 
        ])
    update_property = indented_new_line.join([
        'db_{entity}.{field} = {entity}_data.{field}'.format(entity = entity, field = field)
        for field in fields 
    ])
    init_property = ', '.join([
        '{field} = {entity}_data.{field}'.format(entity = entity, field = field)
        for field in fields
    ])
    # create files
    create_schema(location, module, entity_class, entity, schema_field_declaration)
    create_model(location, module, entity_class, entity, model_field_declaration)
    create_crud(location, module, entity_class, entity, init_property, update_property)
    create_route(location, module, entity, entity_caption)
    create_event(location, module, entity_class, entity)


def create_event(location: str, module: str, entity_class: str, entity: str):
    file_name = os.path.abspath(os.path.join(location, module, 'event.py'))
    lines = generator.read_lines(file_name)
    # look for line with 'def init(' prefix
    insert_index = -1
    for index, line in enumerate(lines):
        if line.startswith('def init('):
            insert_index = index + 1
            break
    if insert_index == -1:
        raise Exception('init function not found in {}'.format(file_name))
    # add event handler
    lines.insert(insert_index, event_template.format(
        entity_class=entity_class,
        entity=entity
    ))
    generator.write_lines(file_name, lines)


def create_route(location: str, module: str, entity: str, entity_caption: str):
    file_name = os.path.abspath(os.path.join(location, module, 'route.py'))
    lines = generator.read_lines(file_name)
    # look for line with 'def init(' prefix
    insert_index = -1
    for index, line in enumerate(lines):
        if line.startswith('def init('):
            insert_index = index + 1
            break
    if insert_index == -1:
        raise Exception('init function not found in {}'.format(file_name))
    lines.insert(insert_index, route_template.format(
        entity=entity,
        entity_caption=entity_caption
    ))
    generator.write_lines(file_name, lines)


def create_schema(location: str, module: str, entity_class: str, entity: str, schema_field_declaration=str):
    # create schema
    file_name = os.path.abspath(os.path.join(location, module, 'schema.py'))
    text = generator.read_text(file_name)
    text += schema_template.format(
        entity_class=entity_class, 
        entity=entity,
        schema_field_declaration=schema_field_declaration
    )
    generator.write_text(file_name, text)


def create_model(location: str, module: str, entity_class: str, entity: str, model_field_declaration: str):
    file_name = os.path.abspath(os.path.join(location, module, 'model.py'))
    text = generator.read_text(file_name)
    text += model_template.format(
        entity_class=entity_class,
        entity=entity,
        model_field_declaration=model_field_declaration
    )
    generator.write_text(file_name, text)


def create_crud(location: str, module: str, entity_class: str, entity: str, init_property: str, update_property: str):
    file_name = os.path.abspath(os.path.join(location, module, 'crud.py'))
    text = generator.read_text(file_name)
    text += crud_template.format(
        entity_class=entity_class,
        entity=entity,
        init_property=init_property,
        update_property=update_property
    )
    generator.write_text(file_name, text)


if __name__ == '__main__':
    create_fast_crud()