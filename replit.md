# Telegram Bot - Kurs Ishi va Maqola Tayyorlash

## Overview

This Telegram bot (@Dotsent_ai_bot) assists users in generating professional coursework and scientific articles using AI (OpenAI GPT-4o Mini). The bot features a balance system, a referral program, and promotional codes. It aims to provide a fast, affordable, and high-quality solution for academic content creation, adhering to specific formatting standards required in Uzbekistan. The project targets students and academics, offering dynamically generated, comprehensive documents.

## User Preferences

I want iterative development. Ask before making major changes. I prefer detailed explanations. Do not make changes to the folder `generated_files/` and the `.env` file.

## System Architecture

The bot is built with `Aiogram 3.x` for Telegram Bot API interaction and `OpenAI API (GPT-4o Mini)` for content generation. It utilizes `SQLite` for database management and `python-docx` for professional DOCX formatting. `LibreOffice CLI` is used for PDF conversion. The system is designed for asynchronous (parallel) processing, allowing multiple users to receive service simultaneously through `asyncio.create_task()` for background tasks and `loop.run_in_executor()` for non-blocking OpenAI API calls.

**UI/UX Decisions:**
- Interactive inline and reply keyboards for user navigation.
- Clear step-by-step FSM (Finite State Machine) for data collection (e.g., F.I.Sh, academic details for coursework; topic, author, supervisor for articles).
- URL buttons for viewing sample documents and accessing support groups.

**Technical Implementations & Feature Specifications:**

- **AI Content Generation:**
    - Uses `gpt-4o-mini` for cost-effectiveness and efficiency.
    - **Coursework:** Generates 35-40 pages (~13,000-15,000 words) across 7 sections (Introduction, 3 Chapters, Conclusion, References, Appendix). Each section is a separate OpenAI request with detailed prompts for depth and length validation. Dynamic plan, table of contents, and references are AI-generated based on the topic.
    - **Scientific Article:** Generates 7-10 pages including title page, multi-lingual abstract (Uzbek, English, Russian), keywords, Introduction, Research Methods, Results & Discussion, Conclusion, and APA-formatted references (15-20 sources).
- **Document Formatting:**
    - Adheres to Uzbekistan's academic standards: Times New Roman 14pt, 1.5 line spacing, specific margins (Left 30mm, Right 15mm, Top/Bottom 20mm), 1.25 cm paragraph indent.
    - Includes dynamic title pages, table of contents, and structured sections in DOCX format.
- **Admin Panel:** Features include mass messaging, user balance management, statistics, system settings (prices, referral bonuses), payment confirmation, and user ban/unban functionality.
- **User Management:** Balance system, referral program, and promotional code application.
- **File Handling:** Automated DOCX and PDF file generation and subsequent deletion to conserve server space.
- **Error Handling:** Graceful error messages and retry mechanisms for content generation.

**System Design Choices:**
- **Modular Structure:** Code is organized into `handlers`, `utils`, `keyboards`, etc., for maintainability.
- **Database Schema:** `SQLite` with tables for `users`, `orders`, `payments`, `promocodes`, and `settings`. Includes fields like `is_blocked` for user banning.
- **Middleware:** `BanCheckMiddleware` to block banned users from bot interaction.
- **Deployment:** Configured for Railway.app with `Procfile`, `requirements.txt`, and automated file cleanup.

## External Dependencies

- **Telegram Bot API:** Accessed via `Aiogram 3.x`.
- **OpenAI API:** For AI-driven content generation, specifically `GPT-4o Mini`.
- **SQLite:** Local database for storing bot data.
- **python-docx:** Python library for creating and modifying Word (.docx) files.
- **LibreOffice CLI:** Command-line tool used for converting DOCX files to PDF.