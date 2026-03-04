import os
import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_db_connection
from psycopg2.extras import RealDictCursor
from decorators import login_required, role_required

anuncios_bp = Blueprint("anuncios", __name__)

@anuncios_bp.route('/gestion-tablon')
@login_required
@role_required("Admin")
def lista_anuncios():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Recuperamos todos los anuncios ordenados por id descendente
        cur.execute("""
            SELECT id, titulo, mensaje, prioridad, 
                   TO_CHAR(fecha_publicacion, 'DD/MM/YYYY HH24:MI') as fecha_publicacion 
            FROM anuncios 
            ORDER BY id DESC
        """)
        anuncios_db = cur.fetchall()
    except Exception as e:
        print(f"Error al consultar anuncios: {e}")
        anuncios_db = []
    finally:
        cur.close()
        conn.close()
    
    return render_template('anuncios.html', anuncios_para_html=anuncios_db)


@anuncios_bp.route('/nuevo', methods=['POST'])
@login_required
@role_required("Admin")
def nuevo_anuncio():
    titulo = request.form.get('titulo')
    mensaje = request.form.get('mensaje')
    prioridad = request.form.get('prioridad', 'normal')

    if not titulo or not mensaje:
        flash("⚠️ Título y mensaje obligatorios.")
        return redirect(url_for('anuncios.lista_anuncios'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO anuncios (titulo, mensaje, prioridad) VALUES (%s, %s, %s)',
            (titulo, mensaje, prioridad)
        )
        conn.commit()
        flash("✅ Anuncio publicado.")
    except Exception as e:
        conn.rollback()
        print(f"Error al insertar: {e}")
        flash("⚠️ Error al guardar.")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('anuncios.lista_anuncios'))


@anuncios_bp.route('/eliminar/<int:id_anuncio>', methods=['POST'])
@login_required
@role_required("Admin")
def eliminar_anuncio(id_anuncio):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM anuncios WHERE id = %s', (id_anuncio,))
        conn.commit()
        flash("✅ Anuncio eliminado.")
    except Exception as e:
        conn.rollback()
        flash("⚠️ No se pudo eliminar.")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('anuncios.lista_anuncios'))


# --------------------- NUEVA FUNCIÓN PARA EDITAR ---------------------
@anuncios_bp.route('/editar/<int:id_anuncio>', methods=['POST'])
@login_required
@role_required("Admin")
def editar_anuncio(id_anuncio):
    """Procesa la actualización de un anuncio existente"""
    titulo = request.form.get('titulo')
    mensaje = request.form.get('mensaje')
    prioridad = request.form.get('prioridad', 'normal')

    if not titulo or not mensaje:
        flash("⚠️ Título y mensaje obligatorios.")
        return redirect(url_for('anuncios.lista_anuncios'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Actualizamos el anuncio por su id
        cur.execute("""
            UPDATE anuncios 
            SET titulo=%s, mensaje=%s, prioridad=%s, fecha_publicacion=NOW() 
            WHERE id=%s
        """, (titulo, mensaje, prioridad, id_anuncio))
        conn.commit()
        flash("✅ Anuncio actualizado.")
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar: {e}")
        flash("⚠️ Error al guardar los cambios.")
    finally:
        cur.close()
        conn.close()
    
    return redirect(url_for('anuncios.lista_anuncios'))
# -----------------------------------------------------------------------