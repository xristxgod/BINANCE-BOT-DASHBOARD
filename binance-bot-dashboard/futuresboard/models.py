
from futuresboard.db_manager import *
from futuresboard.app import login_manager, bcrypt
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))

class UserModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    email_address = db.Column(db.String(256), nullable=False, unique=True)
    password_hash = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    budget = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(32), nullable=False,  server_default='active')
    extra_info = db.Column(db.String(1024), nullable=True, server_default='')

    incomes = db.relationship('IncomeModel', backref='user', lazy=True)
    positions = db.relationship('PositionsModel', backref='user', lazy=True)
    accounts = db.relationship('AccountModel', backref='user', lazy=True)
    orders = db.relationship('OrdersModel', backref='user', lazy=True)

    wallets = db.relationship('UserWalletModel', backref='user', lazy=True)
    transactions = db.relationship('TronTransactionModel', backref='user', lazy=True)
    referrals = db.relationship('ReferralModel', backref='user', lazy=True)
    referrals_profit = db.relationship('ReferralProfitModel', backref='user', lazy=True)
    withdraws = db.relationship('WithdrawModel', backref='user', lazy=True)
    telegram_bot = db.relationship('TelegramBotModel', backref='user', lazy=True)
    password_reset = db.relationship('ResetPasswordModel', backref='user', lazy=True)
    google_authenticator = db.relationship('GoogleAuthenticatorModel', backref='user', lazy=True)

    pass
    
    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f'{str(self.budget)[:-3]}{str(self.budget)[-3:]}$'
        else:
            return f"{self.budget}$"

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class IncomeModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_label = db.Column(db.String(256), nullable=False)
    tranId = db.Column(db.Integer)
    symbol = db.Column(db.String(32), nullable=False)
    incomeType = db.Column(db.String(256), nullable=False)
    income = db.Column(db.Float)
    asset = db.Column(db.String(256), nullable=False)
    info = db.Column(db.String(256), nullable=False)
    time = db.Column(db.Integer)
    tradeId = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))
    pass

class PositionsModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_label = db.Column(db.String(256), nullable=False)
    symbol = db.Column(db.String(32), nullable=False)
    unrealizedProfit = db.Column(db.Float)
    leverage = db.Column(db.Integer)
    entryPrice = db.Column(db.Float)
    positionSide = db.Column(db.String(32), nullable=False)
    positionAmt = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class AccountModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_label = db.Column(db.String(256), nullable=False)
    totalWalletBalance = db.Column(db.Float)
    totalUnrealizedProfit = db.Column(db.Float)
    totalMarginBalance = db.Column(db.Float)
    availableBalance = db.Column(db.Float)
    maxWithdrawAmount = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class OrdersModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_label = db.Column(db.String(256), nullable=False)
    origQty = db.Column(db.Float)
    price = db.Column(db.Float)
    side = db.Column(db.String(32), nullable=False)
    positionSide = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    symbol = db.Column(db.String(32), nullable=False)
    time = db.Column(db.Integer)
    type = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class UserWalletModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(256), nullable=False, unique=True)
    private_key = db.Column(db.String(256), nullable=False, unique=True)
    status = db.Column(db.Boolean, nullable=False, default=False)
    last_activate_time = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class TronTransactionModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    tx_id = db.Column(db.String(256), nullable=False, unique=True)
    amount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class WithdrawModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class ReferralModel(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    referral_code = db.Column(db.String(60), nullable=False, unique=True)
    referrer = db.Column(db.String(60), nullable=True)
    ref_users = db.Column(db.String(2048), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class ReferralProfitModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lvl = db.Column(db.String(4096), nullable=True)
    time = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class TelegramBotModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class ResetPasswordModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(60), nullable=False, unique=True)
    reg_time = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))

class GoogleAuthenticatorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_time = db.Column(db.Integer)
    secret_key = db.Column(db.String(32), nullable=False, unique=True)
    qrcodeData = db.Column(db.String(256), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))