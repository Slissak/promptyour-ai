#!/usr/bin/env python3
"""
Terminal-based chat interface for PromptYour.AI Backend
Interactive command-line chat that connects to the backend API
"""
import asyncio
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
import sys
import os

try:
    import httpx
    import websockets
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
    from rich.text import Text
    from rich import print as rprint
except ImportError as e:
    print(f"Missing required packages. Please install them:")
    print(f"pip install httpx websockets rich")
    print(f"Error: {e}")
    sys.exit(1)


class TerminalChat:
    """Terminal-based chat interface for the PromptYour.AI backend"""
    
    def __init__(self, api_base: str = "http://localhost:8000", use_websocket: bool = True, debug: bool = False, quick_mode: bool = False):
        self.api_base = api_base
        self.use_websocket = use_websocket
        self.debug = debug
        self.quick_mode = quick_mode
        self.console = Console()
        self.user_id = f"terminal_user_{uuid.uuid4().hex[:8]}"
        self.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        self.session_messages = []
        self.first_message_sent = False
        self.conversation_theme = None
        self.conversation_context = None
        self.conversation_audience = None
        self.conversation_response_style = None
        self.message_history = []
        self.chosen_model = None
        self.chosen_provider = None
        
        # Available themes
        self.themes = [
            "academic_help",
            "creative_writing", 
            "coding_programming",
            "business_professional",
            "personal_learning",
            "research_analysis",
            "problem_solving",
            "tutoring_education",
            "general_questions"
        ]
        
        # Available audiences
        self.audiences = [
            "small_kids",        # Ages 5-10
            "teenagers",         # Ages 11-17
            "adults",            # Ages 18-65
            "university_level",  # College/University students and graduates
            "professionals",     # Industry professionals and experts
            "seniors"            # Ages 65+
        ]

        # Available response styles
        self.response_styles = [
            "paragraph_brief",       # Concise, one paragraph response
            "structured_detailed",   # Organized with clear sections and examples
            "instructions_only",     # Direct actions without background
            "comprehensive"          # Full explanation with background and reasoning
        ]
    
    def display_banner(self):
        """Display welcome banner"""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║              🤖 PromptYour.AI Terminal Chat               ║
║                                                           ║
║  Enhanced AI responses through intelligent model routing  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold blue")
        
        # Show connection status
        self.console.print(f"🔗 Connected to: {self.api_base}", style="dim")
        self.console.print(f"👤 User ID: {self.user_id}", style="dim")
        self.console.print(f"💬 Session: {self.conversation_id}", style="dim")
        if self.debug:
            self.console.print("🐛 Debug Mode: Will show Quick + Enhanced + RAW comparison", style="yellow")
        else:
            self.console.print("💬 Normal Mode: Will show Quick + Enhanced (no RAW comparison)", style="cyan")
        if self.quick_mode:
            self.console.print("⚡ Quick Mode: Skipping theme and context questions", style="cyan")
        else:
            self.console.print("🎯 Enhanced Mode: Theme and context questions enabled for better results", style="green")
        self.console.print()

    def start_new_chat(self):
        """Start a new chat session by resetting conversation state"""
        self.conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        self.first_message_sent = False
        self.conversation_theme = None
        self.conversation_context = None
        self.conversation_audience = None
        self.conversation_response_style = None
        self.message_history = []
        self.session_messages = []
        self.chosen_model = None
        self.chosen_provider = None
        
        self.console.print()
        self.console.print("🔄 [bold green]Started new chat session![/bold green]", style="green")
        self.console.print(f"💬 New Session ID: {self.conversation_id}", style="dim")
        self.console.print()

    async def check_backend_status(self) -> bool:
        """Check if backend is running and show status"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check basic health
                health_response = await client.get(f"{self.api_base}/health")
                
                if health_response.status_code != 200:
                    self.console.print(f"❌ Backend health check failed: HTTP {health_response.status_code}", style="red")
                    return False
                
                # Check provider status
                providers_response = await client.get(f"{self.api_base}/api/v1/providers/status")
                
                if providers_response.status_code == 200:
                    provider_data = providers_response.json()["data"]
                    providers = provider_data.get("providers", {})
                    
                    # Create status table
                    table = Table(title="🔌 Provider Status", show_header=True, header_style="bold magenta")
                    table.add_column("Provider", style="cyan", no_wrap=True)
                    table.add_column("Status", justify="center")
                    table.add_column("Details", style="dim")
                    
                    for name, info in providers.items():
                        status = info.get("status", "unknown")
                        status_style = "green" if status == "healthy" else "red" if status == "unhealthy" else "yellow"
                        
                        details = []
                        provider_type = info.get("type", "unknown")
                        
                        if name == "lm_studio":
                            if info.get("loaded_model"):
                                details.append(f"Model: {info['loaded_model']}")
                            details.append(f"Type: {provider_type}")
                        elif name == "openrouter":
                            api_key_configured = info.get("api_key_configured", False)
                            details.append("API Key: ✅" if api_key_configured else "API Key: ❌")
                            details.append(f"Type: {provider_type}")
                        
                        table.add_row(
                            name.replace("_", " ").title(),
                            f"[{status_style}]{status}[/{status_style}]",
                            " | ".join(details) if details else "—"
                        )
                    
                    self.console.print(table)
                    self.console.print()
                    
                return True
                
        except httpx.ConnectError:
            self.console.print("❌ Cannot connect to backend. Make sure it's running!", style="red")
            return False
        except Exception as e:
            self.console.print(f"❌ Error checking backend: {e}", style="red")
            return False

    def get_user_input(self, question: str) -> Optional[Dict[str, Any]]:
        """Get user input with theme selection (only for first message)"""
        if self.first_message_sent:
            # Continue conversation with existing theme/context/audience/response_style and model
            user_data = {
                "question": question,
                "theme": self.conversation_theme or "general_questions",
                "audience": self.conversation_audience or "adults",
                "response_style": self.conversation_response_style or "structured_detailed",
                "context": self.conversation_context,
                "conversation_id": self.conversation_id,
                "message_history": self.message_history
            }
            
            # Force use of the same model for this conversation
            if self.chosen_model and self.chosen_provider:
                user_data["force_model"] = self.chosen_model
                user_data["force_provider"] = self.chosen_provider
                
            return user_data
        
        # First message - get theme and context
        self.console.print("\n" + "─" * 60, style="dim")
        
        # Show theme options
        self.console.print("\n📋 [bold]Available themes:[/bold]")
        for i, theme in enumerate(self.themes, 1):
            display_name = theme.replace("_", " ").title()
            self.console.print(f"  {i:2d}. {display_name}")
        
        # Get theme selection
        while True:
            try:
                theme_choice = Prompt.ask(
                    f"\n🎯 [bold]Choose theme[/bold] (1-{len(self.themes)}, or press Enter for general)",
                    default="9",
                    console=self.console
                )
                
                if theme_choice.strip() == "":
                    selected_theme = "general_questions"
                    break
                
                theme_idx = int(theme_choice) - 1
                if 0 <= theme_idx < len(self.themes):
                    selected_theme = self.themes[theme_idx]
                    break
                else:
                    self.console.print("❌ Invalid choice. Please select 1-9.", style="red")
            except ValueError:
                self.console.print("❌ Please enter a number.", style="red")
        
        # Show audience options
        self.console.print("\n👥 [bold]Available audiences:[/bold]")
        for i, audience in enumerate(self.audiences, 1):
            display_name = audience.replace("_", " ").title()
            if audience == "small_kids":
                display_name += " (Ages 5-10)"
            elif audience == "teenagers":
                display_name += " (Ages 11-17)"
            elif audience == "adults":
                display_name += " (Ages 18-65)"
            elif audience == "university_level":
                display_name += " (College/University)"
            elif audience == "professionals":
                display_name += " (Industry experts)"
            elif audience == "seniors":
                display_name += " (Ages 65+)"
            
            self.console.print(f"  {i:2d}. {display_name}")
        
        # Get audience selection
        while True:
            try:
                audience_choice = Prompt.ask(
                    f"\n👥 [bold]Choose target audience[/bold] (1-{len(self.audiences)}, or press Enter for adults)",
                    default="3",
                    console=self.console
                )

                if audience_choice.strip() == "":
                    selected_audience = "adults"
                    break

                audience_idx = int(audience_choice) - 1
                if 0 <= audience_idx < len(self.audiences):
                    selected_audience = self.audiences[audience_idx]
                    break
                else:
                    self.console.print(f"❌ Invalid choice. Please select 1-{len(self.audiences)}.", style="red")
            except ValueError:
                self.console.print("❌ Please enter a number.", style="red")

        # Show response style options
        self.console.print("\n✨ [bold]Available response styles:[/bold]")
        style_descriptions = {
            "paragraph_brief": "Brief Paragraph - Concise, one paragraph response",
            "structured_detailed": "Structured & Detailed - Organized with clear sections and examples",
            "instructions_only": "Instructions Only - Direct actions without background",
            "comprehensive": "Comprehensive - Full explanation with background and reasoning"
        }
        for i, style in enumerate(self.response_styles, 1):
            self.console.print(f"  {i}. {style_descriptions[style]}")

        # Get response style selection
        while True:
            try:
                style_choice = Prompt.ask(
                    f"\n✨ [bold]Choose response style[/bold] (1-{len(self.response_styles)}, or press Enter for structured & detailed)",
                    default="2",
                    console=self.console
                )

                if style_choice.strip() == "":
                    selected_response_style = "structured_detailed"
                    break

                style_idx = int(style_choice) - 1
                if 0 <= style_idx < len(self.response_styles):
                    selected_response_style = self.response_styles[style_idx]
                    break
                else:
                    self.console.print(f"❌ Invalid choice. Please select 1-{len(self.response_styles)}.", style="red")
            except ValueError:
                self.console.print("❌ Please enter a number.", style="red")

        # Get optional context
        context = Prompt.ask(
            "📝 [dim]Additional context or follow-up questions (optional)[/dim]",
            default="",
            console=self.console
        )
        
        # Store for future messages
        self.conversation_theme = selected_theme
        self.conversation_audience = selected_audience
        self.conversation_response_style = selected_response_style
        self.conversation_context = context if context.strip() else None

        return {
            "question": question,
            "theme": selected_theme,
            "audience": selected_audience,
            "response_style": selected_response_style,
            "context": context if context.strip() else None,
            "conversation_id": self.conversation_id,
            "message_history": self.message_history
        }

    async def send_websocket_message(self, user_input: Dict[str, Any]) -> None:
        """Send message via WebSocket and handle real-time responses"""
        uri = f"ws://localhost:8000/api/v1/ws/chat?user_id={self.user_id}&conversation_id={self.conversation_id}"
        
        try:
            async with websockets.connect(uri) as websocket:
                # Skip welcome message
                await websocket.recv()
                
                # Debug: Print message history being sent
                if self.debug:
                    if user_input.get("message_history"):
                        self.console.print(f"\n[dim]🔍 Debug: Sending {len(user_input['message_history'])} messages in history[/dim]")
                        for i, msg in enumerate(user_input["message_history"][-2:]):  # Show last 2 messages
                            role_emoji = "👤" if msg.get("role") == "user" else "🤖"
                            content_preview = msg.get("content", "")[:50] + "..." if len(msg.get("content", "")) > 50 else msg.get("content", "")
                            self.console.print(f"[dim]  {i+1}. {role_emoji} {msg.get('role', 'unknown')}: {content_preview}[/dim]")
                    else:
                        self.console.print(f"\n[dim]🔍 Debug: No message history being sent (this is normal for first message)[/dim]")

                # Send chat request
                message = {
                    "type": "chat_request",
                    "data": user_input,
                    "debug": self.debug
                }
                
                await websocket.send(json.dumps(message))
                
                # Show processing indicator
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True
                ) as progress:
                    task = progress.add_task("Processing your request...", total=None)
                    
                    # Listen for responses
                    async for response_str in websocket:
                        try:
                            response = json.loads(response_str)
                            msg_type = response.get("type")
                            
                            if msg_type == "processing_step":
                                step_msg = response.get("message", "")
                                progress.update(task, description=step_msg)
                                
                            # Debug prompt handling removed - using debug_comparison instead

                            elif msg_type == "debug_comparison" and self.debug:
                                progress.stop()
                                await self.display_debug_comparison(response.get("data", {}), user_input)
                                progress = Progress(
                                    SpinnerColumn(),
                                    TextColumn("[progress.description]{task.description}"),
                                    console=self.console,
                                    transient=True
                                )
                                task = progress.add_task("Generating final response...", total=None)
                                
                            elif msg_type == "chat_response":
                                progress.stop()
                                # In debug mode, responses are shown in debug_comparison, so skip normal display
                                if not self.debug:
                                    await self.display_response(response.get("data", {}), user_input.get("question"))
                                else:
                                    # Store response data for potential use, but display is handled by debug_comparison
                                    self._last_response_data = response.get("data", {})
                                    self._last_user_question = user_input.get("question")
                                break
                                
                            elif msg_type == "error":
                                progress.stop()
                                error_msg = response.get("message", "Unknown error")
                                self.console.print(f"❌ Error: {error_msg}", style="red")
                                break
                                
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            self.console.print(f"❌ WebSocket error: {e}", style="red")
            self.console.print("🔄 Falling back to HTTP API...", style="yellow")
            await self.send_http_message(user_input)

    async def send_quick_message(self, quick_input: Dict[str, Any]) -> None:
        """Send quick message via HTTP API for one-liner response"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True
                ) as progress:
                    task = progress.add_task("⚡ Getting quick answer...", total=None)

                    response = await client.post(
                        f"{self.api_base}/api/v1/chat/quick",
                        json=quick_input
                    )

                    progress.stop()

                    if response.status_code == 200:
                        data = response.json()

                        # Display quick response
                        self.console.print(f"\n⚡ [bold green]Quick Answer:[/bold green]", style="green")
                        self.console.print(Panel(
                            data.get("content", "No response"),
                            title=f"🤖 {data.get('model_used', 'unknown')} ({data.get('cost', 0):.4f} USD)",
                            title_align="left",
                            border_style="green"
                        ))

                        # Update conversation history
                        self.message_history.append({
                            "role": "user",
                            "content": quick_input["question"]
                        })
                        self.message_history.append({
                            "role": "assistant",
                            "content": data.get("content", ""),
                            "model": data.get("model_used"),
                            "provider": data.get("provider")
                        })

                    else:
                        self.console.print(f"❌ HTTP error: {response.status_code}", style="red")
                        try:
                            error_data = response.json()
                            self.console.print(f"Details: {error_data.get('detail')}", style="dim red")
                        except:
                            pass

        except Exception as e:
            self.console.print(f"❌ Quick request failed: {e}", style="red")

    async def send_enhanced_http_message(self, user_input: Dict[str, Any]) -> None:
        """Send enhanced message via HTTP API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True
                ) as progress:
                    task = progress.add_task("🚀 Generating enhanced response...", total=None)

                    response = await client.post(
                        f"{self.api_base}/api/v1/chat/message",
                        json=user_input
                    )

                    progress.stop()

                    if response.status_code == 200:
                        data = response.json()
                        await self.display_enhanced_response(data, user_input.get("question"))
                    else:
                        self.console.print(f"❌ HTTP error: {response.status_code}", style="red")
                        try:
                            error_data = response.json()
                            self.console.print(f"Details: {error_data.get('detail')}", style="dim red")
                        except:
                            pass

        except Exception as e:
            self.console.print(f"❌ Enhanced request failed: {e}", style="red")

    async def send_http_message(self, user_input: Dict[str, Any]) -> None:
        """Send message via HTTP API (legacy method)"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True
                ) as progress:
                    task = progress.add_task("Sending request to backend...", total=None)

                    # Note: This endpoint might not exist, this is a placeholder
                    # The actual endpoint would need to be implemented in the backend
                    response = await client.post(
                        f"{self.api_base}/api/v1/chat/process",
                        json=user_input
                    )

                    progress.stop()

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("success"):
                            await self.display_response(data.get("data", {}), user_input.get("question"))
                        else:
                            self.console.print(f"❌ Request failed: {data.get('error')}", style="red")
                    else:
                        self.console.print(f"❌ HTTP error: {response.status_code}", style="red")
                        try:
                            error_data = response.json()
                            self.console.print(f"Details: {error_data.get('detail')}", style="dim red")
                        except:
                            pass

        except Exception as e:
            self.console.print(f"❌ HTTP request failed: {e}", style="red")

    # display_debug_prompt method removed - now using display_debug_comparison for better evaluation

    async def display_debug_comparison(self, comparison_data: Dict[str, Any], original_input: Dict[str, Any] = None) -> None:
        """Display enhanced vs RAW response comparison in debug mode"""
        enhanced = comparison_data.get("enhanced_response", {})
        # Try both "raw_response" (new) and "basic_response" (legacy) for backwards compatibility
        raw = comparison_data.get("raw_response", comparison_data.get("basic_response", {}))
        model = comparison_data.get("model", "unknown")
        provider = comparison_data.get("provider", "unknown")
        user_question = comparison_data.get("user_question", "")

        self.console.print()
        self.console.print("[bold cyan]🔬 DEBUG MODE: Enhanced vs RAW Response Comparison[/bold cyan]")
        self.console.print()

        # Show user question
        if user_question:
            question_panel = Panel(
                user_question,
                title="❓ User Question",
                title_align="left",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(question_panel)

        # Show model selection info (from display_response logic)
        enhanced_response = comparison_data.get("enhanced_response", {})
        cost = enhanced_response.get("cost", 0)
        response_time = enhanced_response.get("response_time_ms", 0)

        # Get model selection reasoning from comparison data
        reasoning = enhanced_response.get("reasoning", "")

        # Determine provider style and emoji
        provider_emoji = "🏠" if provider == "lm_studio" else "☁️" if provider == "openrouter" else "🤖"
        provider_style = "bold blue" if provider == "lm_studio" else "bold magenta" if provider == "openrouter" else "bold cyan"

        # Show model selection
        model_announcement = f"{provider_emoji} [bold cyan]MODEL SELECTED BY ALGORITHM:[/bold cyan] [{provider_style}]{provider.upper()}[/{provider_style}] → [bold yellow]{model}[/bold yellow]"
        self.console.print(Panel(
            model_announcement,
            title="🎯 Smart Model Selection",
            title_align="left",
            border_style=provider_style,
            padding=(0, 1)
        ))

        # Show reasoning if available
        if reasoning:
            reasoning_panel = Panel(
                f"[dim]Algorithm reasoning: {reasoning}[/dim]",
                title="🧠 Why This Model?",
                title_align="left",
                border_style="dim",
                padding=(0, 1)
            )
            self.console.print(reasoning_panel)

        # Show cost and response time
        metadata_table = Table.grid(padding=1)
        metadata_table.add_column(style="dim", justify="right")
        metadata_table.add_column(style="bold")

        cost_style = "green" if cost == 0 else "yellow"
        metadata_table.add_row("💰 Cost:", f"[{cost_style}]${cost:.6f}[/{cost_style}]")
        metadata_table.add_row("⚡ Response Time:", f"[cyan]{response_time}ms[/cyan]")

        metadata_panel = Panel(
            metadata_table,
            title="📊 Performance Metrics",
            title_align="left",
            border_style="dim",
            padding=(0, 1)
        )
        self.console.print(metadata_panel)
        self.console.print()

        # Create comparison table
        comparison_table = Table(
            title=f"📊 Response Comparison using {model}",
            show_header=True,
            header_style="bold magenta"
        )
        comparison_table.add_column("Metric", style="cyan", width=20)
        comparison_table.add_column("Enhanced (Our System)", style="green", width=40)
        comparison_table.add_column("Raw Model (No System Prompt)", style="yellow", width=40)

        # Add metrics
        comparison_table.add_row(
            "Tokens Used",
            str(enhanced.get("tokens_used", 0)),
            str(raw.get("tokens_used", 0))
        )
        comparison_table.add_row(
            "Cost",
            f"${enhanced.get('cost', 0):.6f}",
            f"${raw.get('cost', 0):.6f}"
        )
        comparison_table.add_row(
            "Response Time",
            f"{enhanced.get('response_time_ms', 0)}ms",
            f"{raw.get('response_time_ms', 0)}ms"
        )

        self.console.print(comparison_table)

        # Show prompts used (full prompts, no truncation)
        enhanced_prompt = enhanced.get("system_prompt", "")
        raw_prompt = raw.get("system_prompt", None)

        prompts_table = Table(
            title="🎯 System Prompts Used",
            show_header=True,
            header_style="bold cyan"
        )
        prompts_table.add_column("Enhanced System Prompt", style="green", width=50)
        prompts_table.add_column("Raw Model Input (No System Prompt)", style="yellow", width=50)

        # Handle no system prompt case but show user message if available
        if raw_prompt is None or raw_prompt == "":
            raw_user_msg = raw.get("user_message", "")
            if raw_user_msg and len(raw_user_msg) > 100:
                raw_msg_preview = raw_user_msg[:100] + "..."
            else:
                raw_msg_preview = raw_user_msg or "[dim italic]NO SYSTEM PROMPT - Only raw user question[/dim italic]"
            raw_prompt_display = f"[dim italic]NO SYSTEM PROMPT[/dim italic]\n\nUser message sent:\n{raw_msg_preview}"
        else:
            raw_prompt_display = raw_prompt

        prompts_table.add_row(enhanced_prompt, raw_prompt_display)

        self.console.print(prompts_table)

        # Show enhanced response first
        self.console.print()
        enhanced_response_panel = Panel(
            enhanced.get("content", ""),
            title="✨ Enhanced Response (Our System)",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(enhanced_response_panel)

        # Show raw model response after
        self.console.print()
        raw_response_panel = Panel(
            raw.get("content", "[dim italic]No RAW response received[/dim italic]"),
            title="🤖 Raw Model Response (No System Prompt)",
            title_align="left",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(raw_response_panel)

        # Analysis summary
        token_diff = enhanced.get("tokens_used", 0) - raw.get("tokens_used", 0)
        cost_diff = enhanced.get("cost", 0) - raw.get("cost", 0)

        analysis_text = []
        if token_diff > 0:
            analysis_text.append(f"Enhanced used {token_diff} more tokens (+{(token_diff/raw.get('tokens_used', 1)*100):.1f}%)")
        elif token_diff < 0:
            analysis_text.append(f"Enhanced used {abs(token_diff)} fewer tokens ({(abs(token_diff)/raw.get('tokens_used', 1)*100):.1f}% less)")
        else:
            analysis_text.append("Both responses used same number of tokens")

        if cost_diff > 0:
            analysis_text.append(f"Enhanced cost ${cost_diff:.6f} more")
        elif cost_diff < 0:
            analysis_text.append(f"Enhanced cost ${abs(cost_diff):.6f} less")
        else:
            analysis_text.append("Both responses had same cost")

        analysis_panel = Panel(
            "\n".join(analysis_text),
            title="📈 Quick Analysis",
            title_align="left",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(analysis_panel)

        self.console.print("[dim]💡 Note: RAW response receives ONLY the user's question (no system prompt, no history). Enhanced response uses intelligent system prompting.[/dim]")
        self.console.print("[dim]📋 The enhanced response (shown above) will be used as the final answer.[/dim]")

        # Store conversation history (same logic as display_response)
        if user_question:
            self.message_history.append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.now().isoformat()
            })

        # Store enhanced response in history
        enhanced_content = enhanced.get("content", "")
        if enhanced_content:
            self.message_history.append({
                "role": "assistant",
                "content": enhanced_content,
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "provider": provider
            })

        # Store the chosen model and provider for this conversation (first time only)
        if not self.chosen_model and not self.chosen_provider:
            self.chosen_model = model
            self.chosen_provider = provider

        self.console.print()

    async def display_enhanced_response(self, response_data: Dict[str, Any], user_question: str = None) -> None:
        """Display enhanced AI response, optionally with RAW comparison in debug mode"""
        content = response_data.get("content", "")
        model_used = response_data.get("model_used", "unknown")
        provider = response_data.get("provider", "unknown")
        cost = response_data.get("cost", 0)
        response_time = response_data.get("response_time_ms", 0)
        reasoning = response_data.get("reasoning", "")
        system_prompt = response_data.get("system_prompt", "")
        raw_response = response_data.get("raw_response", None)

        # NOTE: Don't add user question to history - it's already there from quick response

        # If debug mode is enabled AND raw_response exists, show comparison
        if self.debug and raw_response:
            # Build comparison data structure similar to WebSocket debug mode
            comparison_data = {
                "enhanced_response": {
                    "content": content,
                    "tokens_used": response_data.get("tokens_used", 0),
                    "cost": cost,
                    "response_time_ms": response_time,
                    "system_prompt": system_prompt,
                    "reasoning": reasoning
                },
                "raw_response": {
                    "content": raw_response,
                    "tokens_used": 0,  # Not provided separately
                    "cost": 0,  # Not provided separately
                    "response_time_ms": 0,  # Not provided separately
                    "system_prompt": "",  # Always empty for RAW
                    "user_message": user_question or ""
                },
                "model": model_used,
                "provider": provider,
                "user_question": user_question or ""
            }

            # Display the comparison
            await self.display_debug_comparison(comparison_data)
        else:
            # Normal mode: just display the enhanced response
            # Create prominent model/provider header
            self.console.print()

            # Determine provider style and emoji
            provider_emoji = "🏠" if provider == "lm_studio" else "☁️" if provider == "openrouter" else "🤖"
            provider_style = "bold blue" if provider == "lm_studio" else "bold magenta" if provider == "openrouter" else "bold cyan"
            cost_style = "green" if cost == 0 else "yellow"

            # Create enhanced response header
            self.console.print(f"🚀 [bold green]Enhanced Response:[/bold green] {provider_emoji} [{provider_style}]{provider.upper()}[/{provider_style}] → [bold yellow]{model_used}[/bold yellow]", style="green")

            # Display the enhanced content
            self.console.print(Panel(
                Markdown(content) if content.strip() else "No response content",
                title=f"🤖 Enhanced Response (${cost:.4f} USD, {response_time}ms)",
                title_align="left",
                border_style="blue"
            ))

            # Show reasoning for enhanced model selection
            if reasoning:
                self.console.print(Panel(
                    reasoning,
                    title="🎯 Why this model was selected",
                    title_align="left",
                    border_style="yellow"
                ))

        # Add the enhanced response to conversation history (replacing the quick response)
        # Remove the last assistant message (quick response) and replace with enhanced
        if self.message_history and self.message_history[-1]["role"] == "assistant":
            self.message_history[-1] = {
                "role": "assistant",
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "model": model_used,
                "provider": provider
            }
        else:
            # Fallback: add enhanced response normally
            self.message_history.append({
                "role": "assistant",
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "model": model_used,
                "provider": provider
            })

        self.console.print()

    async def display_response(self, response_data: Dict[str, Any], user_question: str = None) -> None:
        """Display the AI response in a nice format"""
        content = response_data.get("content", "")
        model_used = response_data.get("model_used", "unknown")
        provider = response_data.get("provider", "unknown")
        cost = response_data.get("cost", 0)
        response_time = response_data.get("response_time_ms", 0)
        reasoning = response_data.get("reasoning", "")
        
        # Store the user message that led to this response
        if user_question:
            self.message_history.append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.now().isoformat()
            })
        
        # Create prominent model/provider header
        self.console.print()
        
        # Determine provider style and emoji
        provider_emoji = "🏠" if provider == "lm_studio" else "☁️" if provider == "openrouter" else "🤖"
        provider_style = "bold blue" if provider == "lm_studio" else "bold magenta" if provider == "openrouter" else "bold cyan"
        cost_style = "green" if cost == 0 else "yellow"
        
        # Create prominent model selection announcement
        if self.chosen_model == model_used and self.chosen_provider == provider:
            # Same model as chosen for this conversation
            model_announcement = f"{provider_emoji} [bold green]CONTINUING WITH CHOSEN MODEL:[/bold green] [{provider_style}]{provider.upper()}[/{provider_style}] → [bold yellow]{model_used}[/bold yellow]"
            panel_title = "🔄 Same Model (Conversation Consistency)"
        else:
            # New model selection
            model_announcement = f"{provider_emoji} [bold cyan]MODEL SELECTED BY ALGORITHM:[/bold cyan] [{provider_style}]{provider.upper()}[/{provider_style}] → [bold yellow]{model_used}[/bold yellow]"
            panel_title = "🎯 Smart Model Selection"
            
        self.console.print(Panel(
            model_announcement,
            title=panel_title,
            title_align="left",
            border_style=provider_style,
            padding=(0, 1)
        ))
        
        # Add model selection reasoning if available
        if reasoning:
            reasoning_panel = Panel(
                f"[dim]Algorithm reasoning: {reasoning}[/dim]",
                title="🧠 Why This Model?",
                title_align="left",
                border_style="dim",
                padding=(0, 1)
            )
            self.console.print(reasoning_panel)
        
        # Response metadata table
        metadata_table = Table.grid(padding=1)
        metadata_table.add_column(style="dim", justify="right")
        metadata_table.add_column(style="bold")
        
        # Emphasize cost with different styling
        cost_display = f"[{cost_style}]${cost:.6f}[/{cost_style}]"
        if cost == 0:
            cost_display += " [dim](FREE local inference)[/dim]"
        
        metadata_table.add_row("💰 Cost:", cost_display)
        metadata_table.add_row("⏱️  Response Time:", f"{response_time}ms")
        
        # Display response with enhanced title
        response_title = f"💬 Response from {model_used} via {provider.title()}"
        response_panel = Panel(
            Markdown(content),
            title=response_title,
            title_align="left",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(metadata_table)
        self.console.print()
        self.console.print(response_panel)
        
        # Store in session history
        self.session_messages.append({
            "timestamp": datetime.now().isoformat(),
            "model": model_used,
            "provider": provider,
            "cost": cost,
            "response_time": response_time,
            "content_length": len(content)
        })
        
        # Store conversation history for memory
        self.message_history.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "model": model_used,
            "provider": provider
        })
        
        # Store the chosen model and provider for this conversation (first time only)
        if not self.chosen_model and not self.chosen_provider:
            self.chosen_model = model_used
            self.chosen_provider = provider
        
        # Ask for rating
        await self.collect_rating(response_data.get("message_id"))

    async def collect_rating(self, message_id: str) -> None:
        """Collect user rating for the response"""
        if not message_id:
            return
            
        try:
            rating = Prompt.ask(
                "\n⭐ [bold]Rate this response[/bold] (1-5, or press Enter to skip)",
                default="",
                console=self.console
            )
            
            if rating.strip():
                rating_num = int(rating)
                if 1 <= rating_num <= 5:
                    feedback = Prompt.ask(
                        "💬 [dim]Optional feedback[/dim]",
                        default="",
                        console=self.console
                    )
                    
                    # Send rating (placeholder - would need actual endpoint)
                    self.console.print(f"✅ Rating submitted: {rating_num}/5", style="green")
                    
        except (ValueError, KeyboardInterrupt):
            pass

    def display_help(self):
        """Display help information"""
        help_text = """
[bold cyan]🆘 Terminal Chat Help[/bold cyan]

[bold]Enhanced Chat Mode (Default):[/bold]
• First message: Choose theme, audience, and context for tailored AI responses
• Continuing messages: Theme/audience/context automatically remembered
• Conversation maintains memory and context throughout session
• Rate responses to improve the system

[bold]Quick Chat Mode (--quick flag):[/bold]
• Type your question and press Enter
• Skips theme, audience, and context questions for faster responses
• Uses general theme and adult audience by default
• Still maintains conversation memory

[bold]Available Themes:[/bold]
• Academic Help - homework, study questions
• Creative Writing - stories, poems, creative content
• Coding/Programming - technical questions, debugging
• Business/Professional - work-related queries
• Personal Learning - learning new topics
• Research/Analysis - research help, analysis
• Problem Solving - general problem solving
• Tutoring/Education - teaching and explanations
• General Questions - everything else

[bold]Target Audiences:[/bold]
• Small Kids (Ages 5-10) - simple language, friendly tone, kid-friendly examples
• Teenagers (Ages 11-17) - age-appropriate, engaging, relatable examples
• Adults (Ages 18-65) - professional, clear, practical examples
• University Level - academic language, scholarly examples, critical thinking
• Professionals - technical language, industry examples, expert insights
• Seniors (Ages 65+) - clear, respectful, patient explanations

[bold]Special Commands:[/bold]
• /help - Show this help
• /status - Check backend and provider status
• /stats - Show session statistics
• /new - Start a new chat session (reset conversation history)
• /clear - Clear screen
• /quit or /exit - Exit the chat

[bold]Tips:[/bold]
• Be specific in your questions for better results
• Use context to provide background information
• Try different themes to see how responses change
• The system automatically chooses the best model for your query
        """
        
        self.console.print(Panel(help_text, title="📖 Help", border_style="blue"))

    def display_session_stats(self):
        """Display session statistics"""
        if not self.session_messages:
            self.console.print("📊 No messages in this session yet.", style="dim")
            return
            
        total_messages = len(self.session_messages)
        total_cost = sum(msg["cost"] for msg in self.session_messages)
        avg_response_time = sum(msg["response_time"] for msg in self.session_messages) / total_messages
        
        providers_used = {}
        models_used = {}
        
        for msg in self.session_messages:
            provider = msg["provider"]
            model = msg["model"]
            
            providers_used[provider] = providers_used.get(provider, 0) + 1
            models_used[model] = models_used.get(model, 0) + 1
        
        stats_table = Table(title="📊 Session Statistics", show_header=True)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="bold")
        
        stats_table.add_row("Total Messages", str(total_messages))
        stats_table.add_row("Total Cost", f"${total_cost:.6f}")
        stats_table.add_row("Avg Response Time", f"{avg_response_time:.0f}ms")
        stats_table.add_row("Most Used Provider", max(providers_used.items(), key=lambda x: x[1])[0] if providers_used else "None")
        stats_table.add_row("Most Used Model", max(models_used.items(), key=lambda x: x[1])[0] if models_used else "None")
        
        self.console.print(stats_table)

    async def run(self):
        """Main chat loop"""
        self.display_banner()
        
        # Check backend status
        if not await self.check_backend_status():
            return
        
        # Show help
        self.console.print("💡 Type [bold]/help[/bold] for commands, or start chatting!", style="dim")
        
        while True:
            try:
                # Display prompt with context info for continuing conversations
                if self.first_message_sent and self.conversation_theme:
                    theme_display = self.conversation_theme.replace("_", " ").title()
                    prompt_text = f"\n💭 [bold cyan]Continue conversation[/bold cyan] [dim]({theme_display})[/dim]"
                else:
                    prompt_text = "\n💭 [bold cyan]Your question[/bold cyan]"
                
                raw_input = Prompt.ask(prompt_text, console=self.console).strip()
                
                if not raw_input:
                    continue
                
                # Handle special commands
                if raw_input.lower() in ['/quit', '/exit', '/q']:
                    self.console.print("👋 Goodbye!", style="bold blue")
                    break
                elif raw_input.lower() == '/help':
                    self.display_help()
                    continue
                elif raw_input.lower() == '/status':
                    await self.check_backend_status()
                    continue
                elif raw_input.lower() == '/stats':
                    self.display_session_stats()
                    continue
                elif raw_input.lower() == '/new':
                    self.start_new_chat()
                    continue
                elif raw_input.lower() == '/clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.display_banner()
                    continue
                
                # Handle regular chat
                if raw_input.startswith('/'):
                    self.console.print(f"❌ Unknown command: {raw_input}", style="red")
                    self.console.print("Type [bold]/help[/bold] for available commands.", style="dim")
                    continue
                
                # NEW TWO-TIER SYSTEM: Quick answer first, then option for enhanced

                # Step 1: Send quick request with conversation history
                quick_input = {
                    "question": raw_input,
                    "conversation_id": self.conversation_id,
                    "message_history": self.message_history
                }

                # Force use of the same model for this conversation if already chosen
                if self.chosen_model and self.chosen_provider:
                    quick_input["force_model"] = self.chosen_model
                    quick_input["force_provider"] = self.chosen_provider

                # Send quick request and get one-liner response
                await self.send_quick_message(quick_input)

                # Step 2: Ask user if they want an enhanced response
                if not self.quick_mode:  # Only ask for enhancement in regular mode
                    wants_enhanced = Confirm.ask(
                        "\n🎯 [bold yellow]Would you like a more detailed, tailored response?[/bold yellow]",
                        console=self.console,
                        default=False
                    )

                    if wants_enhanced:
                        # Get theme/audience selection and send enhanced request
                        user_input = self.get_user_input(raw_input)
                        if user_input:
                            # Include the updated message history (now has the quick Q&A)
                            user_input["message_history"] = self.message_history
                            self.console.print("\n🚀 [bold green]Generating enhanced response...[/bold green]", style="green")
                            if self.use_websocket:
                                await self.send_websocket_message(user_input)
                            else:
                                await self.send_enhanced_http_message(user_input)
                    else:
                        # User satisfied with quick response, just continue
                        pass
                else:
                    # In quick mode, don't offer enhanced responses
                    pass

                # Mark first message as sent
                self.first_message_sent = True
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Chat interrupted. Goodbye!", style="bold blue")
                break
            except Exception as e:
                self.console.print(f"\n❌ Unexpected error: {e}", style="red")
                continue


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PromptYour.AI Terminal Chat")
    parser.add_argument("--api", default="http://localhost:8000", help="Backend API URL")
    parser.add_argument("--http-only", action="store_true", help="Use HTTP only (no WebSocket)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode to show enhanced vs raw model comparison")
    parser.add_argument("--quick", action="store_true", help="Quick mode: skip theme and context questions")
    
    args = parser.parse_args()
    
    chat = TerminalChat(
        api_base=args.api,
        use_websocket=not args.http_only,
        debug=args.debug,
        quick_mode=args.quick
    )
    
    await chat.run()


if __name__ == "__main__":
    asyncio.run(main())