# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bot Menú Glotón D.C. - A Telegram bot for managing restaurant lunch menus. Built with `python-telegram-bot` and JSON file persistence.

## Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
cd bot && python bot.py
```

## Architecture

### Data Layer (`bot/menu_logic/`)

All data managers inherit from `GestorBase` (`base.py`) which provides:
- CRUD operations: `create()`, `update()`, `delete()`, `get_all()`, `get_by_id()`
- Auto-incrementing IDs with reindexing on delete (RN03)
- JSON persistence in `data/` directory

Data managers:
- `GestorAlmuerzos` - Lunch items with category support
- `GestorEntradas` - Appetizers/starters
- `GestorAcompanamientos` - Side dishes
- `GestorCategorias` - Categories with prices

### Bot Logic (`bot/bot.py`)

Single-file bot using:
- `ConversationHandler` for multi-step flows (register, update, generate menu)
- `CallbackQueryHandler` for inline keyboard navigation
- State machine states defined as constants (e.g., `ESTADO_NOMBRE`, `ESTADO_GEN_ESPECIALES`)

### Data Files (`data/`)

JSON files mirror manager names: `almuerzos.json`, `entradas.json`, `acompanamientos.json`, `categorias.json`

## Business Rules

- RN01: Only one menu per day
- RN02: No duplicate lunches in catalog
- RN03: IDs reindex automatically when records are deleted

## Environment

Required `.env` file:
```
TOKEN=your_telegram_bot_token
```