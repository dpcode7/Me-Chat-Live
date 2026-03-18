from database import SessionLocal, User, generate_id

def create_user():
    print("\n--- 🛠️ ME CHAT: VIP Admin Creator ---")
    name = input("👤 Enter Full Name: ")
    dob = input("📅 Enter DOB (e.g. 09-sep-2006): ")
    gender = input("🚻 Enter Gender (Male/Female/Other) [Press Enter for Male]: ").strip()
    
    if not gender:
        gender = "Male"

    if not name or not dob:
        print("❌ Error: Name and DOB are required!")
        return

    db = SessionLocal()
    try:
        secret_key = generate_id("KEY")
        public_id = generate_id("ME")
        
        new_user = User(full_name=name, dob=dob, gender=gender, secret_key=secret_key, public_id=public_id)
        db.add(new_user)
        db.commit()
        
        print("\n✅ ACCOUNT CREATED SUCCESSFULLY, BOSS!")
        print("="*45)
        print(f"🔑 Secret Key (For Login) : {secret_key}")
        print(f"🆔 Public ID (For Chat)   : {public_id}")
        print(f"👤 Full Name              : {name}")
        print(f"🚻 Gender                 : {gender}")
        print("="*45 + "\n")
    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_user()