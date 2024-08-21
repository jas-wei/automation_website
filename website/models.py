from . import db
from flask_login import UserMixin

# Define Preferences model
class Preferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    overlay_opacity = db.Column(db.String(50), default="0.000")
    watermark_opacity = db.Column(db.String(50), default="0.000")
    watermark_label = db.Column(db.String(50), default="Enter Text")
    font_size = db.Column(db.String(50), default="30")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

# Define User model with preferences helper methods
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    
    # One-to-one relationship with Preferences
    preference = db.relationship('Preferences', uselist=False, backref='user', cascade="all, delete-orphan")

    # Helper method to get or create preferences
    def get_preference(self):
        if not self.preference:
            # If user has no preferences, create default preferences
            self.preference = Preferences(
                user_id=self.id,
                overlay_opacity="0.000",
                watermark_opacity="0.000",
                watermark_label="Enter Text",
                font_size="30"
            )
            db.session.add(self.preference)
            db.session.commit()
        return self.preference

    # Helper method to update preferences
    def update_preference(self, overlay_opacity=None, watermark_opacity=None, watermark_label=None, font_size=None):
        # Ensure that preferences exist before updating
        pref = self.get_preference()  # This ensures we get existing preferences or create defaults

        # Update only the provided fields
        if overlay_opacity is not None:
            pref.overlay_opacity = overlay_opacity
        if watermark_opacity is not None:
            pref.watermark_opacity = watermark_opacity
        if watermark_label is not None:
            pref.watermark_label = watermark_label
        if font_size is not None:
            pref.font_size = font_size

        db.session.commit()  # Save the changes to the database
