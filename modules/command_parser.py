"""
Command Parser Module
Parses recognized speech into executable commands
"""

class CommandParser:
    def __init__(self):
        """Initialize command parser"""
        self.commands = {
            'status': {
                'keywords': ['status', 'الحالة', 'حالة', 'كيفك'],
                'description': 'Get system status',
                'action': 'STATUS'
            },
            'hello': {
                'keywords': ['hello', 'hi', 'hey', 'مرحبا', 'أهلا', 'سلام'],
                'description': 'Greeting',
                'action': 'HELLO'
            },
            'help': {
                'keywords': ['help', 'مساعدة', 'ساعد', 'أوامر'],
                'description': 'Show available commands',
                'action': 'HELP'
            },
            'info': {
                'keywords': ['info', 'معلومات', 'عني', 'من أنت'],
                'description': 'Show system information',
                'action': 'INFO'
            },
            'stop': {
                'keywords': ['stop', 'توقف', 'قف', 'أوقف'],
                'description': 'Stop current operation',
                'action': 'STOP'
            }
        }
    
    def parse(self, text):
        """
        Parse text and return command
        
        Args:
            text: Input text from speech recognition
        
        Returns:
            Dictionary with command details or None
        """
        if not text:
            return None
        
        # Normalize text
        text_lower = text.lower().strip()
        
        # Search for matching command
        for cmd_name, cmd_info in self.commands.items():
            for keyword in cmd_info['keywords']:
                if keyword in text_lower:
                    return {
                        'name': cmd_name,
                        'action': cmd_info['action'],
                        'description': cmd_info['description'],
                        'input': text
                    }
        
        return None
    
    def get_command(self, command_name):
        """Get command details by name"""
        return self.commands.get(command_name)
    
    def list_commands(self):
        """Get list of all available commands"""
        return list(self.commands.keys())
    
    def get_help_text(self):
        """Get help text with all commands"""
        help_text = "📋 Available Commands:\n"
        for cmd_name, cmd_info in self.commands.items():
            keywords = ", ".join(cmd_info['keywords'][:3])
            help_text += f"  • {cmd_name}: {cmd_info['description']}\n"
            help_text += f"    Keywords: {keywords}\n"
        return help_text
    
    def add_command(self, command_name, keywords, description, action):
        """
        Add a new command
        
        Args:
            command_name: Name of the command
            keywords: List of keywords that trigger this command
            description: Command description
            action: Action code
        """
        self.commands[command_name] = {
            'keywords': keywords,
            'description': description,
            'action': action
        }
        print(f"✅ Command '{command_name}' added")
    
    def remove_command(self, command_name):
        """Remove a command"""
        if command_name in self.commands:
            del self.commands[command_name]
            print(f"✅ Command '{command_name}' removed")
        else:
            print(f"❌ Command '{command_name}' not found")
    
    def print_commands(self):
        """Print all commands in a formatted way"""
        print("\n" + "="*50)
        print("📋 AVAILABLE COMMANDS")
        print("="*50)
        for cmd_name, cmd_info in self.commands.items():
            print(f"\n🔹 {cmd_name.upper()}")
            print(f"   Description: {cmd_info['description']}")
            print(f"   Keywords: {', '.join(cmd_info['keywords'])}")
            print(f"   Action: {cmd_info['action']}")
        print("\n" + "="*50)
