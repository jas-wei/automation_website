from . import db  # Replace 'your_flask_app' with the name of your Flask app's module
from .models import Preferences, User  # Replace 'your_flask_app' with the correct module for models

def cleanup_preferences():
    # Get all users
    users = User.query.all()

    for user in users:
        # Get all preferences associated with the user
        user_preferences = Preferences.query.filter_by(user_id=user.id).all()

        if len(user_preferences) > 1:
            print(f"User {user.id} has {len(user_preferences)} preferences, cleaning up duplicates...")

            # Keep the first preference and delete the rest
            primary_preference = user_preferences[0]

            for duplicate_preference in user_preferences[1:]:
                print(f"Deleting duplicate preference with ID {duplicate_preference.id}")
                db.session.delete(duplicate_preference)

            # Commit after deleting the duplicates
            db.session.commit()

        elif len(user_preferences) == 0:
            print(f"User {user.id} has no preferences, creating default preferences...")

            # If the user has no preferences, create default preferences
            new_preference = Preferences(
                overlay_opacity="0.000",
                watermark_opacity="0.000",
                watermark_label="Enter Text",
                font_size="30",
                user_id=user.id
            )
            db.session.add(new_preference)
            db.session.commit()

    print("Preferences cleanup complete.")

if __name__ == "__main__":
    with your_flask_app.app.app_context():  # Replace 'your_flask_app' with your app module
        cleanup_preferences()
