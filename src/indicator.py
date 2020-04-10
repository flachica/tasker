#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of todotxt-indicator
#
# Copyright (c) 2020 Lorenzo Carbonell Cerezo <a.k.a. atareao>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('AppIndicator3', '0.1')
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import AppIndicator3
from gi.repository import GdkPixbuf
import sys
import os
import webbrowser
from pathlib import Path
from config import _
from graph import Graph
from preferences import Preferences
import config
from configurator import Configuration

def round(value):
    return int(value * 10000) / 10000.0


class Indicator(object):

    def __init__(self):

        self.indicator = AppIndicator3.Indicator.new(
            'todotxt-indicator',
            'todotxt-indicator',
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.load_preferences()
        self.indicator.set_menu(self.build_menu())
        self.indicator.set_label('', '')
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.set_icon(True)
        Gtk.main()

    def set_icon(self, active=True):
        if active:
            if self.theme_light:
                icon = config.ICON_ACTIVED_LIGHT
            else:
                icon = config.ICON_ACTIVED_DARK
        else:
            if self.theme_light:
                icon = config.ICON_PAUSED_LIGHT
            else:
                icon = config.ICON_PAUSED_DARK
        self.indicator.set_icon(icon)

    def load_preferences(self):
        self.configuration = Configuration()
        preferences = self.configuration.get('preferences')
        self.theme_light = preferences['theme-light']
        self.todos = preferences['todos']
        self.dones = preferences['dones']
        todo_file = Path(os.path.expanduser(preferences['todo-file']))
        if not todo_file.exists():
            if not todo_file.parent.exists():
                os.makedirs(todo_file.parent)
            todo_file.touch()
        self.todo_file = todo_file.as_posix()
        done_file = Path(os.path.expanduser(preferences['done-file']))
        if not done_file.exists():
            if not done_file.parent.exists():
                os.makedirs(done_file.parent)
            done_file.touch()
        self.done_file = done_file.as_posix()
        self.set_icon(True)

    def on_popped(self, widget, display):
        pass

    def build_menu(self):
        menu = Gtk.Menu()
        menu.connect('draw', self.on_popped)

        self.menu_todos = []
        for i in range(0, self.todos):
            self.menu_todos.append(Gtk.MenuItem.new_with_label(''))
            menu.append(self.menu_todos[i])

        menu.append(Gtk.SeparatorMenuItem())

        self.menu_dones = []
        for i in range(0, self.dones):
            self.menu_dones.append(Gtk.MenuItem.new_with_label(''))
            menu.append(self.menu_dones[i])

        menu.append(Gtk.SeparatorMenuItem())

        menu_add_todo = Gtk.MenuItem.new_with_label(_('Add todo'))
        menu.append(menu_add_todo)

        menu.append(Gtk.SeparatorMenuItem())
        menu_show_statistics = Gtk.MenuItem.new_with_label(
            _('Statistics'))
        menu_show_statistics.connect('activate', self.show_statistics)
        menu.append(menu_show_statistics)

        menu.append(Gtk.SeparatorMenuItem())

        menu_preferences = Gtk.MenuItem.new_with_label(_('Preferences'))
        menu_preferences.connect('activate', self.show_preferences)
        menu.append(menu_preferences)

        menus_help = Gtk.MenuItem.new_with_label(_('Help'))
        menus_help.set_submenu(self.get_help_menu())
        menu.append(menus_help)

        menu.append(Gtk.SeparatorMenuItem())

        menu_quit = Gtk.MenuItem. new_with_label(_('Quit'))
        menu_quit.connect('activate', self.quit)
        menu.append(menu_quit)
        menu.show_all()
        return menu

    def show_change(self, widget):
        change = Change()
        response = change.run()
        change.destroy()

    def show_preferences(self, widget):
        widget.set_sensitive(False)
        preferences = Preferences()
        response = preferences.run()
        if response == Gtk.ResponseType.ACCEPT:
            preferences.save()
            self.load_preferences()
            self.set_icon(True)
        preferences.destroy()
        widget.set_sensitive(True)

    def show_statistics(self, widget):
        widget.set_sensitive(False)

        title = _('Currency indicator')
        subtitle = _('Rates')
        configuration = Configuration()
        preferences = self.configuration.get('preferences')

        mc = CURRENCIES[self.main_currency]
        currencies = []
        for i in range(0, 5):
            print(self.currencies[i])
            currencies.append(CURRENCIES[self.currencies[i]])
        days = []
        c0 = []
        c1 = []
        c2 = []
        c3 = []
        c4 = []
        for aday in self.exchange.data:
            days.append(aday['date'])
            mc = aday[self.main_currency.lower()]
            c0.append(round(aday[self.currencies[0].lower()] / mc))
            c1.append(round(aday[self.currencies[1].lower()] / mc))
            c2.append(round(aday[self.currencies[2].lower()] / mc))
            c3.append(round(aday[self.currencies[3].lower()] / mc))
            c4.append(round(aday[self.currencies[4].lower()] / mc))

        graph = Graph(title, subtitle, currencies, days, c0, c1, c2, c3, c4)
        graph.run()
        graph.destroy()
        widget.set_sensitive(True)

    def get_help_menu(self):
        help_menu = Gtk.Menu()

        homepage_item = Gtk.MenuItem.new_with_label(_('Homepage'))
        homepage_item.connect(
            'activate',
            lambda x: webbrowser.open(
                'http://www.atareao.es/aplicacion/todotxt-indicator/'))
        help_menu.append(homepage_item)

        help_item = Gtk.MenuItem.new_with_label(_('Get help online...'))
        help_item.connect(
            'activate',
            lambda x: webbrowser.open(
                'http://www.atareao.es/aplicacion/todotxt-indicator/'))
        help_menu.append(help_item)

        translate_item = Gtk.MenuItem.new_with_label(_(
            'Translate this application...'))
        translate_item.connect(
            'activate',
            lambda x: webbrowser.open(
                'http://www.atareao.es/aplicacion/todotxt-indicator/'))
        help_menu.append(translate_item)

        bug_item = Gtk.MenuItem.new_with_label(_('Report a bug...'))
        bug_item.connect(
            'activate',
            lambda x: webbrowser.open('https://github.com/atareao\
/todotxt-indicator/issues'))
        help_menu.append(bug_item)

        help_menu.append(Gtk.SeparatorMenuItem())

        twitter_item = Gtk.MenuItem.new_with_label(_('Found me in Twitter'))
        twitter_item.connect(
            'activate',
            lambda x: webbrowser.open('https://twitter.com/atareao'))
        help_menu.append(twitter_item)
        #
        github_item = Gtk.MenuItem.new_with_label(_('Found me in GitHub'))
        github_item.connect(
            'activate',
            lambda x: webbrowser.open('https://github.com/atareao'))
        help_menu.append(github_item)

        mastodon_item = Gtk.MenuItem.new_with_label(_('Found me in Mastodon'))
        mastodon_item.connect(
            'activate',
            lambda x: webbrowser.open('https://mastodon.social/@atareao'))
        help_menu.append(mastodon_item)

        about_item = Gtk.MenuItem.new_with_label(_('About'))
        about_item.connect('activate', self.menu_about_response)

        help_menu.append(Gtk.SeparatorMenuItem())

        help_menu.append(about_item)
        return help_menu

    def menu_about_response(self, widget):
        widget.set_sensitive(False)
        ad = Gtk.AboutDialog()
        ad.set_name(config.APPNAME)
        ad.set_version(config.VERSION)
        ad.set_copyright('Copyrignt (c) 2020\nLorenzo Carbonell')
        ad.set_comments(_('Currency Indicator'))
        ad.set_license('''
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.''')
        ad.set_website('')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors(['Lorenzo Carbonell Cerezo <a.k.a. atareao>'])
        ad.set_translator_credits('Lorenzo Carbonell Cerezo <a.k.a. atareao>')
        ad.set_documenters(['Lorenzo Carbonell Cerezo <a.k.a. atareao>'])
        ad.set_artists(['Freepik <https://www.flaticon.com/authors/freepik>'])
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(config.ICON))
        ad.set_icon(GdkPixbuf.Pixbuf.new_from_file(config.ICON))
        ad.set_program_name(config.APPNAME)

        monitor = Gdk.Display.get_primary_monitor(Gdk.Display.get_default())
        scale = monitor.get_scale_factor()
        monitor_width = monitor.get_geometry().width / scale
        monitor_height = monitor.get_geometry().height / scale
        width = ad.get_preferred_width()[0]
        height = ad.get_preferred_height()[0]
        ad.move((monitor_width - width)/2, (monitor_height - height)/2)

        ad.run()
        ad.destroy()
        widget.set_sensitive(True)

    def quit(self, menu_item):
        Gtk.main_quit()
        # If Gtk throws an error or just a warning, main_quit() might not
        # actually close the app
        sys.exit(0)


def main():
    Indicator()


if __name__ == '__main__':
    main()