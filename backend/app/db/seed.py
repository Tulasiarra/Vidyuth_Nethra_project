import os
import csv
from datetime import datetime
from sqlalchemy import func
from app.db.connection import engine, SessionLocal, Base
from app.db.models import Home, Device, DeviceDailySummary, HomeDailySummary, User, HomeBaseline, TrainingRecord

def seed_database():
    # 1. Create tables if they do not exist
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if database is already seeded
        if db.query(Home).first():
            print("Database already seeded. Skipping seeder.")
            return

        print("Seeding database...")
        dataset_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "dataset")
        
        # Ensure default demo user exists
        demo_user = db.query(User).filter_by(email="arjun@example.com").first()
        if not demo_user:
            # hashed bcrypt password for 'demo1234'
            # (using a precomputed hash to avoid importing bcrypt during seeding if not needed, but bcrypt is installed)
            # $2b$12$Z0H7nU.dJ7C55sZt1.e4sOkYn5fK1Gq0X6P7w.nE3Vz1Lz/sV/9G6
            demo_user = User(
                name="Arjun",
                email="arjun@example.com",
                phone_number="9876543210",
                password_hash="$2b$12$Z0H7nU.dJ7C55sZt1.e4sOkYn5fK1Gq0X6P7w.nE3Vz1Lz/sV/9G6", # demo1234
                notification_preferences="all",
                is_verified=True
            )
            db.add(demo_user)
            db.commit()
            print("Demo user Arjun created.")

        # 2. Seed Homes
        homes_csv = os.path.join(dataset_dir, "homes.csv")
        homes_map = {}
        if os.path.exists(homes_csv):
            print("Reading homes...")
            with open(homes_csv, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                homes_to_insert = []
                for row in reader:
                    h_id = str(row["home_id"])
                    rate = float(row["electricity_rate"])
                    target = float(row["target_monthly_bill"])
                    home = Home(
                        id=h_id,
                        name=row["home_name"],
                        location="Bangalore, Karnataka",
                        electricity_rate=rate,
                        target_monthly_bill=target,
                        home_type="Independent House" if int(h_id) % 3 == 0 else "Apartment" if int(h_id) % 3 == 1 else "Villa",
                        user_email="arjun@example.com"
                    )
                    homes_to_insert.append(home)
                    homes_map[h_id] = rate
                
                db.bulk_save_objects(homes_to_insert)
                db.commit()
                print(f"Seeded {len(homes_to_insert)} homes.")
        else:
            print(f"Homes CSV not found at {homes_csv}")
            return

        # 3. Seed Devices
        devices_csv = os.path.join(dataset_dir, "devices.csv")
        devices_map = {}
        if os.path.exists(devices_csv):
            print("Reading devices...")
            with open(devices_csv, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                devices_to_insert = []
                for row in reader:
                    d_id = str(row["device_id"])
                    h_id = str(row["home_id"])
                    watts = float(row["rated_watts"])
                    device = Device(
                        id=d_id,
                        home_id=h_id,
                        name=f"{row['brand']} {row['device_type']}",
                        device_type=row["device_type"],
                        brand=row["brand"],
                        model=row["model"],
                        room_name=row["room_name"],
                        rated_watts=watts,
                        installation_date="2024-01-01",
                        status="OFF",
                        is_enabled=True
                    )
                    devices_to_insert.append(device)
                    devices_map[d_id] = (watts, h_id)
                
                db.bulk_save_objects(devices_to_insert)
                db.commit()
                print(f"Seeded {len(devices_to_insert)} devices.")
        else:
            print(f"Devices CSV not found at {devices_csv}")
            return

        # 4. Seed Device Daily Summaries
        summaries_csv = os.path.join(dataset_dir, "device_daily_summary.csv")
        if os.path.exists(summaries_csv):
            print("Reading device daily summaries (this might take a few seconds)...")
            with open(summaries_csv, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                summaries_to_insert = []
                
                # To track aggregated home daily consumption
                home_daily_agg = {} # {(home_id, date): [total_energy, total_cost]}
                
                count = 0
                for row in reader:
                    d_id = str(row["device_id"])
                    h_id = str(row["home_id"])
                    date_str = row["date"]
                    runtime = float(row["runtime_hours"])
                    
                    # Lookup watts and rate
                    watts, _ = devices_map.get(d_id, (100.0, h_id))
                    rate = homes_map.get(h_id, 7.0)
                    
                    energy = (runtime * watts) / 1000.0
                    cost = energy * rate
                    
                    summary_dict = {
                        "home_id": h_id,
                        "device_id": d_id,
                        "date": date_str,
                        "runtime_hours": runtime,
                        "energy_consumed_kwh": energy,
                        "cost_incurred": cost
                    }
                    summaries_to_insert.append(summary_dict)
                    
                    # Aggregate for home summaries
                    key = (h_id, date_str)
                    if key not in home_daily_agg:
                        home_daily_agg[key] = [0.0, 0.0]
                    home_daily_agg[key][0] += energy
                    home_daily_agg[key][1] += cost
                    
                    count += 1
                    if len(summaries_to_insert) >= 50000:
                        db.bulk_insert_mappings(DeviceDailySummary, summaries_to_insert)
                        db.commit()
                        summaries_to_insert = []
                        print(f"Inserted {count} device summary rows...")
                
                if summaries_to_insert:
                    db.bulk_insert_mappings(DeviceDailySummary, summaries_to_insert)
                    db.commit()
                print(f"Total {count} device summary rows seeded.")

                # 5. Seed Home Daily Summaries
                print("Inserting home daily summaries...")
                home_summaries_to_insert = []
                for (h_id, date_str), (total_energy, total_cost) in home_daily_agg.items():
                    home_summaries_to_insert.append({
                        "home_id": h_id,
                        "date": date_str,
                        "total_energy_kwh": total_energy,
                        "total_cost": total_cost
                    })
                
                # Insert in chunks
                chunk_size = 20000
                for i in range(0, len(home_summaries_to_insert), chunk_size):
                    db.bulk_insert_mappings(HomeDailySummary, home_summaries_to_insert[i:i+chunk_size])
                    db.commit()
                print(f"Seeded {len(home_summaries_to_insert)} home daily summaries.")

        else:
            print(f"Summaries CSV not found at {summaries_csv}")

        # 6. Seed Home Baselines (Calculate averages from summaries for all homes/device types)
        print("Calculating baseline averages...")
        baselines = db.query(
            Home.id, Device.device_type, func.avg(DeviceDailySummary.runtime_hours)
        ).join(
            Device, Home.id == Device.home_id
        ).join(
            DeviceDailySummary, Device.id == DeviceDailySummary.device_id
        ).group_by(
            Home.id, Device.device_type
        ).all()
        
        baselines_to_insert = []
        for h_id, d_type, avg_runtime in baselines:
            baselines_to_insert.append(
                HomeBaseline(
                    home_id=h_id,
                    device_type=d_type,
                    baseline_runtime_hours=float(avg_runtime or 0.0)
                )
            )
        db.bulk_save_objects(baselines_to_insert)
        db.commit()
        print(f"Calculated and seeded {len(baselines_to_insert)} device baselines across homes.")

        # 7. Seed Training Records
        import json
        training_csv = os.path.join(dataset_dir, "training_dataset.csv")
        if os.path.exists(training_csv):
            print("Reading training dataset...")
            with open(training_csv, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                records_to_insert = []
                count = 0
                for row in reader:
                    h_id = str(row["home_id"])
                    date_str = row["date"]
                    
                    # Split row into features and targets
                    features = {}
                    targets = {}
                    for k, v in row.items():
                        if k in ["home_id", "date"]:
                            continue
                        if k.startswith("next_day_"):
                            targets[k] = float(v) if v else 0.0
                        else:
                            try:
                                if "." in v:
                                    features[k] = float(v)
                                else:
                                    features[k] = int(v)
                            except ValueError:
                                features[k] = v
                                
                    records_to_insert.append({
                        "home_id": h_id,
                        "date": date_str,
                        "features_json": json.dumps(features),
                        "targets_json": json.dumps(targets)
                    })
                    
                    count += 1
                    if len(records_to_insert) >= 20000:
                        db.bulk_insert_mappings(TrainingRecord, records_to_insert)
                        db.commit()
                        records_to_insert = []
                        print(f"Inserted {count} training records...")
                        
                if records_to_insert:
                    db.bulk_insert_mappings(TrainingRecord, records_to_insert)
                    db.commit()
                print(f"Total {count} training records seeded.")
        else:
            print(f"Training dataset CSV not found at {training_csv}")

        print("Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
