from fastmcp import FastMCP
import sqlite3
import json
from typing import Dict, Any, List
from datetime import datetime

# FastMCP server oluştur
mcp = FastMCP("database-agent")

# Veritabanı bağlantısı
DB_PATH = "agent_database.db"

def init_database():
    """Veritabanını ve örnek tabloları oluştur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Örnek tablo: students
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_name TEXT,
            profession TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Örnek tablo: teachers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT,
            experience_years INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Örnek tablo: products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Örnek tablo: employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT,
            position TEXT,
            salary REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Veritabanını başlat
init_database()

@mcp.tool()
def insert_to_table(table_name: str, data: Dict[str, Any]) -> str:
    """
    Veritabanındaki bir tabloya veri ekler
    
    Args:
        table_name: Veri eklenecek tablo adı (students, teachers, products, employees)
        data: Eklenecek veri (örn: {"name": "Enes", "parent_name": "Gönül", "profession": "Mühendis"})
    
    Returns:
        İşlem sonucu mesajı
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Sütun isimlerini ve değerlerini ayır
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(query, values)
        
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        
        result = {
            "success": True,
            "message": f"✅ Veri {table_name} tablosuna başarıyla eklendi",
            "row_id": row_id,
            "inserted_data": data
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"❌ Hata: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_table_info(table_name: str) -> str:
    """
    Bir tablonun yapısını (sütunlar ve tipleri) getirir
    
    Args:
        table_name: Bilgisi alınacak tablo adı
    
    Returns:
        Tablo yapısı bilgisi
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if not columns:
            return json.dumps({
                "error": f"'{table_name}' tablosu bulunamadı"
            }, ensure_ascii=False)
        
        schema = {
            "table": table_name,
            "columns": [
                {
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "primary_key": bool(col[5])
                }
                for col in columns
            ]
        }
        
        conn.close()
        return json.dumps(schema, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
def list_all_tables() -> str:
    """
    Veritabanındaki tüm tabloları listeler
    
    Returns:
        Tablo isimleri listesi
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return json.dumps({
            "tables": tables,
            "count": len(tables)
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
def query_table(table_name: str, limit: int = 10) -> str:
    """
    Tablodaki son kayıtları getirir
    
    Args:
        table_name: Sorgulanacak tablo adı
        limit: Getirilecek maksimum kayıt sayısı (varsayılan: 10)
    
    Returns:
        Tablo kayıtları
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        # Sütun isimlerini al
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Sonuçları dictionary listesine çevir
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        conn.close()
        
        return json.dumps({
            "table": table_name,
            "count": len(results),
            "records": results
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
def delete_record(table_name: str, record_id: int) -> str:
    """
    Tablodan belirtilen ID'ye sahip kaydı siler
    
    Args:
        table_name: Tablo adı
        record_id: Silinecek kaydın ID'si
    
    Returns:
        İşlem sonucu
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (record_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            return json.dumps({
                "success": True,
                "message": f"✅ ID {record_id} olan kayıt {table_name} tablosundan silindi"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "success": False,
                "message": f"⚠️ ID {record_id} olan kayıt bulunamadı"
            }, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
def update_record(table_name: str, record_id: int, data: Dict[str, Any]) -> str:
    """
    Tablodaki bir kaydı günceller
    
    Args:
        table_name: Tablo adı
        record_id: Güncellenecek kaydın ID'si
        data: Güncellenecek veriler (örn: {"name": "Yeni İsim", "profession": "Yeni Meslek"})
    
    Returns:
        İşlem sonucu
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # SET kısmını oluştur
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values()) + [record_id]
        
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if updated_count > 0:
            return json.dumps({
                "success": True,
                "message": f"✅ ID {record_id} olan kayıt güncellendi",
                "updated_fields": data
            }, ensure_ascii=False)
        else:
            return json.dumps({
                "success": False,
                "message": f"⚠️ ID {record_id} olan kayıt bulunamadı"
            }, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

if __name__ == "__main__":
    # FastMCP sunucusunu başlat
    mcp.run()