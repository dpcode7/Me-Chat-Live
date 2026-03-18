from database import SessionLocal, User

def search_users():
    print("\n--- 🔍 ME CHAT: Admin Scanner ---")
    print("👉 Enter Public ID to search (e.g. ME-123456)")
    print("👉 Leave blank and press ENTER to see ALL users with their Secret Keys")
    search_id = input("\n🆔 Enter Public ID: ").strip()

    db = SessionLocal()
    try:
        if search_id == "":
            users = db.query(User).all()
            print("\n" + "="*70)
            print("📋 ALL REGISTERED USERS (ADMIN VIEW)")
            print("="*70)
            if not users:
                print("⚠️ Database is empty, Tycoon!")
            else:
                for u in users:
                    print(f"Public ID: {u.public_id} | Secret: {u.secret_key} | Name: {u.full_name} | Gender: {u.gender}")
            print("="*70 + "\n")
        else:
            user = db.query(User).filter(User.public_id == search_id).first()
            if user:
                print("\n✅ USER FOUND!")
                print("="*40)
                print(f"🆔 Public ID   : {user.public_id}")
                print(f"🔑 Secret Key  : {user.secret_key}  <-- (Hidden from others)")
                print(f"👤 Name        : {user.full_name}")
                print(f"📅 DOB         : {user.dob}")
                print(f"🚻 Gender      : {user.gender}")
                print("="*40 + "\n")
            else:
                print(f"\n❌ ERROR: No user found with Public ID '{search_id}'!\n")
    finally:
        db.close()

if __name__ == "__main__":
    search_users()