# 📁 production_bot.py
import os
import logging
import sqlite3
import requests
import schedule
import time
import threading
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد logging متقدم
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_production.log'),
        logging.StreamHandler()
    ]
)

class البوت_الإنتاجي:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.weather_api_key = os.getenv('WEATHER_API_KEY')
        self.port = int(os.environ.get('PORT', 8443))
        self.webhook_url = os.getenv('WEBHOOK_URL', '')
        
        if not self.token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN مطلوب!")
        
        # إعداد التطبيق
        self.application = Application.builder().token(self.token).build()
        
        # إعداد قاعدة البيانات
        self.إعداد_قاعدة_بيانات_متقدمة()
        
        # إعداد المعالجات
        self.إعداد_المعالجات_الإنتاجية()
        
        # بدء المهام النظامية
        self.بدء_النظام()
        
        logging.info("✅ البوت الإنتاجي جاهز للتشغيل!")
    
    def إعداد_قاعدة_بيانات_متقدمة(self):
        """إعداد قاعدة بيانات متقدمة مع نسخ احتياطي"""
        try:
            self.conn = sqlite3.connect('production_bot.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # جدول المستخدمين المحسن
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS المستخدمين (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_premium BOOLEAN DEFAULT 0,
                    settings JSON DEFAULT '{}'
                )
            ''')
            
            # جدول السجلات النظامية
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS سجلات_النظام (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            self.سجل_النظام("INFO", "قاعدة البيانات جاهزة")
            
        except Exception as e:
            self.سجل_النظام("ERROR", f"خطأ في قاعدة البيانات: {e}")
            raise
    
    def سجل_النظام(self, level, message):
        """تسجيل أحداث النظام"""
        try:
            self.cursor.execute(
                'INSERT INTO سجلات_النظام (level, message) VALUES (?, ?)',
                (level, message)
            )
            self.conn.commit()
        except:
            pass  # تجنب الأخطاء الدورية
    
    def إعداد_المعالجات_الإنتاجية(self):
        """إعداد معالجات للأوضاع الإنتاجية"""
        
        # الأوامر الأساسية
        self.application.add_handler(CommandHandler("start", self.بدء_إنتاجي))
        self.application.add_handler(CommandHandler("status", self.حالة_النظام))
        self.application.add_handler(CommandHandler("logs", self.عرض_السجلات))
        self.application.add_handler(CommandHandler("backup", self.نسخ_احتياطي))
        
        # معالجة الرسائل
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.معالجة_إنتاجية))
        
        # معالجة الأخطاء
        self.application.add_error_handler(self.معالجة_الأخطاء_العالمية)
    
    async def بدء_إنتاجي(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إصدار إنتاجي من أمر /start"""
        user = update.effective_user
        
        رسالة = f"""
        🚀 **مرحباً بك في البوت الإنتاجي!** {user.first_name}
        
        ✅ **الحالة:** البوت يعمل على خادم إنتاجي
        ⏰ **الوقت:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        📊 **النظام:** مستقر وجاهز للعمل 24/7
        
        🔧 **الأوامر المتاحة:**
        /status - حالة النظام
        /logs - سجلات النظام (للمطور)
        /backup - نسخ احتياطي
        
        💡 البوت الآن يعمل بشكل مستمر دون توقف!
        """
        
        await update.message.reply_text(رسالة)
        self.سجل_النظام("INFO", f"مستخدم جديد: {user.first_name}")
    
    async def حالة_النظام(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض حالة النظام"""
        try:
            # إحصائيات النظام
            self.cursor.execute('SELECT COUNT(*) FROM المستخدمين')
            total_users = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM المستخدمين WHERE date(last_active) = date("now")')
            active_today = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(*) FROM سجلات_النظام WHERE date(timestamp) = date("now")')
            today_logs = self.cursor.fetchone()[0]
            
            # معلومات الخادم
            import psutil
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            رسالة_الحالة = f"""
            📊 **حالة النظام - تقرير حي**
            
            👥 **المستخدمين:**
            • الإجمالي: {total_users}
            • النشطون اليوم: {active_today}
            
            💾 **الخادم:**
            • وحدة المعالجة: {cpu_usage}%
            • الذاكرة: {memory.percent}%
            • السجلات اليوم: {today_logs}
            
            ⏰ **زمن التشغيل:**
            • الوقت: {datetime.now().strftime("%H:%M:%S")}
            • التاريخ: {datetime.now().strftime("%Y-%m-%d")}
            
            ✅ **الحالة:** مستقرة وجاهزة
            """
            
            await update.message.reply_text(رسالة_الحالة)
            
        except Exception as e:
            await update.message.reply_text("❌ حدث خطأ في جلب حالة النظام")
            self.سجل_النظام("ERROR", f"خطأ في حالة النظام: {e}")
    
    async def نسخ_احتياطي(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إنشاء نسخة احتياطية من البيانات"""
        try:
            user_id = update.effective_user.id
            if user_id != 123456789:  # استبدل بـ ID حسابك
                await update.message.reply_text("❐ هذا الأمر للمطور فقط")
                return
            
            # إنشاء نسخة احتياطية
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "users_count": self.جعدد_المستخدمين(),
                "backup_type": "manual"
            }
            
            # حفظ النسخة الاحتياطية
            with open(f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json", 'w') as f:
                import json
                json.dump(backup_data, f, indent=2)
            
            await update.message.reply_text("✅ تم إنشاء نسخة احتياطية بنجاح")
            self.سجل_النظام("INFO", "نسخة احتياطية تم إنشاؤها يدوياً")
            
        except Exception as e:
            await update.message.reply_text("❌ فشل في إنشاء النسخة الاحتياطية")
            self.سجل_النظام("ERROR", f"خطأ في النسخ الاحتياطي: {e}")
    
    def جعدد_المستخدمين(self):
        """الحصول على عدد المستخدمين"""
        self.cursor.execute('SELECT COUNT(*) FROM المستخدمين')
        return self.cursor.fetchone()[0]
    
    def بدء_النظام(self):
        """بدء المهام النظامية"""
        def المهام_الخلفية():
            # جدولة المهام النظامية
            schedule.every(10).minutes.do(self.الفحص_الصحي)
            schedule.every().hour.do(self.تنظيف_السجلات)
            schedule.every().day.at("02:00").do(self.نسخ_احتياطي_تلقائي)
            
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=المهام_الخلفية, daemon=True)
        thread.start()
        self.سجل_النظام("INFO", "المهام الخلفية بدأت العمل")
    
    def الفحص_الصحي(self):
        """فحص صحة النظام"""
        try:
            # فحص قاعدة البيانات
            self.cursor.execute('SELECT 1')
            
            # فحص الاتصال بالإنترنت
            requests.get('https://api.telegram.org', timeout=5)
            
            self.سجل_النظام("DEBUG", "الفحص الصحي: النظام يعمل بشكل طبيعي")
            
        except Exception as e:
            self.سجل_النظام("ERROR", f"فحص صحي فاشل: {e}")
    
    def نسخ_احتياطي_تلقائي(self):
        """نسخ احتياطي تلقائي يومي"""
        try:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "users_count": self.جعدد_المستخدمين(),
                "backup_type": "auto"
            }
            
            filename = f"backup_auto_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                import json
                json.dump(backup_data, f, indent=2)
            
            self.سجل_النظام("INFO", f"نسخة احتياطية تلقائية: {filename}")
            
        except Exception as e:
            self.سجل_النظام("ERROR", f"خطأ في النسخ التلقائي: {e}")
    
    async def معالجة_الأخطاء_العالمية(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة جميع الأخطاء الغير متوقعة"""
        try:
            raise context.error
        except Exception as e:
            self.سجل_النظام("ERROR", f"خطأ غير متوقع: {e}")
            
            if update and update.effective_user:
                try:
                    await update.message.reply_text(
                        "❌ حدث خطأ غير متوقع. تم تسجيله وسيتم إصلاحه قريباً."
                    )
                except:
                    pass
    
    def تشغيل_وضع_الإنتاج(self):
        """تشغيل البوت في وضع الإنتاج مع webhook"""
        if not self.webhook_url:
            logging.warning("WEBHOOK_URL غير محدد. سيتم تشغيل البوت بنظام polling.")
            self.application.run_polling()
            return

        # تشغيل webhook
        logging.info(f"✅ تشغيل البوت عبر Webhook على {self.webhook_url}/{self.token}")
        self.application.run_webhook(
            listen="0.0.0.0",
            port=self.port,
            url_path=self.token,  # تيليجرام سيرسل POST إلى /<TOKEN>
            webhook_url=f"{self.webhook_url}/{self.token}"  # رابط خارجي HTTPS
        )
