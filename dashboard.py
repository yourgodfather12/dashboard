from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio

def create_app(secret_key):
    app = Flask(__name__)
    app.secret_key = secret_key

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    # Placeholder for the bot object, to be imported from bot.py
    from bot import bot

    # User authentication
    class User(UserMixin):
        def __init__(self, id):
            self.id = id

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username == os.getenv('ADMIN_USERNAME') and password == os.getenv('ADMIN_PASSWORD'):
                user = User(id=1)
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # Dashboard routes
    @app.route('/')
    @login_required
    def index():
        # Example data for bot performance
        bot_performance = {
            'servers': len(bot.guilds) if bot else 0,
            'commands_processed': 1234,  # Placeholder
            'messages_processed': 5678,  # Placeholder
        }
        return render_template('index.html', bot_performance=bot_performance, bot_ready=bot and bot.is_ready())

    @app.route('/servers')
    @login_required
    def servers():
        guilds = bot.guilds if bot else []
        return render_template('servers.html', bot_ready=bot and bot.is_ready(), guilds=guilds)

    @app.route('/commands')
    @login_required
    def commands():
        slash_commands = []
        if bot:
            for command in bot.tree.walk_commands():
                slash_commands.append({
                    'name': command.name,
                    'description': command.description,
                    'cog': command.cog_name if hasattr(command, 'cog_name') else 'N/A'
                })
        return render_template('commands.html', slash_commands=slash_commands)

    @app.route('/guild/<int:guild_id>')
    @login_required
    async def guild(guild_id):
        guild = bot.get_guild(guild_id)
        invites = await guild.invites() if guild else []
        return render_template('guild.html', guild=guild, invites=invites)

    @app.route('/create_invite/<int:guild_id>/<int:channel_id>', methods=['POST'])
    @login_required
    async def create_invite(guild_id, channel_id):
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        if not channel:
            flash('Channel not found')
            return redirect(url_for('guild', guild_id=guild_id))
        try:
            invite = await channel.create_invite(max_age=3600, max_uses=1)
            flash(f'Invite created: {invite.url}')
        except Exception as e:
            flash(f'Error creating invite: {str(e)}')
        return redirect(url_for('guild', guild_id=guild_id))

    @app.route('/delete_invite/<int:guild_id>/<string:invite_code>', methods=['POST'])
    @login_required
    async def delete_invite(guild_id, invite_code):
        invite = discord.utils.get(await bot.cached_invites(), code=invite_code)
        if not invite:
            flash('Invite not found')
            return redirect(url_for('guild', guild_id=guild_id))
        try:
            await invite.delete()
            flash('Invite deleted')
        except Exception as e:
            flash(f'Error deleting invite: {str(e)}')
        return redirect(url_for('guild', guild_id=guild_id))

    return app

if __name__ == '__main__':
    secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
    app = create_app(secret_key)
    app.run(debug=True)
