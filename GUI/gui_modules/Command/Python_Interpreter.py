import sys
from PyQt5.QtWidgets import (
    QApplication, QPlainTextEdit, QCompleter, QListView)
from PyQt5.QtCore import Qt, QEvent, QStringListModel, pyqtSignal
from PyQt5.QtGui import (QTextCursor, QFont, QSyntaxHighlighter,
                         QTextCharFormat, QColor)
from PyQt5.QtCore import QRegularExpression, QRect
import io
import contextlib
from collections import deque
import builtins

from code import InteractiveInterpreter


class CompleterPopup(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, e):
        print("OK")
        return super().keyPressEvent(e)

    def currentChanged(self, current, previous):
        print("IN")
        return super().currentChanged(current, previous)


class PythonCompleter(QCompleter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setCaseSensitivity(Qt.CaseSensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.completion_model = QStringListModel()
        self.setModel(self.completion_model)
        self.update_completion_context()

        self.popup_widget = CompleterPopup()
        self.setPopup(self.popup_widget)

    def update_completion_context(self):
        builtin_items = dir(builtins)
        all_items = list(set(builtin_items))
        self.completion_model.setStringList(all_items)

    def triggerCompletion(self, word: str, rect: QRect):
        # TODO:processing . expression
        # if '.' in line_text[:cursor_pos]:
        #     parts = line_text[:cursor_pos].rsplit('.', 1)
        #     base = parts[0]
        #     try:
        #         obj = eval(base, globals())
        #         members = [m for m in dir(obj) if not m.startswith('_')]
        #         self.completion_model.setStringList(members)
        #         self.completer.setCompletionPrefix(parts[-1])
        #         cr = self.console.cursorRect()
        #         cr.setWidth(self.completer.popup().sizeHintForColumn(0)
        #                     + self.completer.popup().verticalScrollBar().sizeHint().width())
        #         self.completer.complete(cr)
        #         return
        #     except:
        #         pass

        self.setCompletionPrefix(word)
        rect.setWidth(200)
        self.complete(rect)


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        # add keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))  # blue
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if',
            'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass',
            'raise', 'return', 'try', 'while', 'with', 'yield', 'None', 'True', 'False'
        ]
        for word in keywords:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append(
                (QRegularExpression(pattern), keyword_format))

        # add string format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(163, 21, 21))  # bronzing
        self.highlighting_rules.append(
            (QRegularExpression(r'\".*\"'), string_format))
        self.highlighting_rules.append(
            (QRegularExpression(r'\'.*\''), string_format))

        # add number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0, 128, 0))  # green
        self.highlighting_rules.append(
            (QRegularExpression(r'\b[0-9]+\b'), number_format))

        # add comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(128, 128, 128))  # grey
        comment_format.setFontItalic(True)
        self.highlighting_rules.append(
            (QRegularExpression(r'#[^\n]*'), comment_format))

        # add function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(42, 0, 255))  # deep bule
        function_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegularExpression(r'\bdef\s+(\w+)'), function_format))

        # add class format
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(88, 24, 69))  # violet
        class_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append(
            (QRegularExpression(r'\bclass\s+(\w+)'), class_format))

    def highlightBlock(self, text):
        # highlight for block code
        for pattern, fmt in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(),
                               match.capturedLength(), fmt)

        #
        self.setCurrentBlockState(0)

        # triple quotes
        triple_double = QRegularExpression(r'"""[^"]*"""')
        triple_single = QRegularExpression(r"'''[^']*'''")

        for pattern in [triple_double, triple_single]:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(),
                               QTextCharFormat().setForeground(QColor(163, 21, 21)))


class PythonInterpreter(QPlainTextEdit, InteractiveInterpreter):
    """
    Python interpreter widget
    """
    prompt = ">>> "
    continue_prompt = "... "
    prompt_len = len(prompt)

    triggerComplete = pyqtSignal(str, QRect)

    def __init__(self, parent=None):
        QPlainTextEdit.__init__(self, parent)
        InteractiveInterpreter.__init__(self, globals())

        self._resetbuffer()
        self.history = deque(maxlen=1000)
        self.history_index = None
        self.buffer = []  # buffer for unfinished cmd
        self.prompt_pos = -1
        self.more = False  # tag for need more cmd
        self.has_completed = False  # TODO: delete this

        self.highlighter = PythonHighlighter(self.document())
        self.completer = PythonCompleter(self)
        self.completer.setWidget(self)

        self.initUI()

        # ready and print welcome message
        self.write_output(
            f"Python {sys.version} on {sys.platform}\nWelcome to EDA-Q\n")
        self.write_prompt()

    def initUI(self):
        # set self
        self.setCursorWidth(12)
        self.setFont(QFont('Courier New', 12))
        self.setReadOnly(False)
        self.installEventFilter(self)

        self.cursorPositionChanged.connect(self.handleCursorPositionChanged)
        self.textChanged.connect(self.handleTextChanged)
        self.triggerComplete.connect(self.completer.triggerCompletion)
        self.completer.activated.connect(self.handleInsertCompletion)

    def handleCursorPositionChanged(self):
        """Handle cursor position always after prompt."""
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        if cursor_pos < self.prompt_pos:
            cursor.setPosition(self.prompt_pos, QTextCursor.KeepAnchor if cursor.hasSelection(
            ) else QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)

        self.ensureCursorVisible()

    def handleTextChanged(self):
        """Handle text changed."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.WordLeft,
                            QTextCursor.MoveMode.KeepAnchor)
        last_word = cursor.selectedText()
        cursor_rect = self.cursorRect()
        self.triggerComplete.emit(last_word, cursor_rect)

    def handleInsertCompletion(self, completion):
        """Insert completion."""
        cursor = self.textCursor()
        cursor.setPosition(self.prompt_pos, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(completion, self.textCursor().charFormat())
        self.moveCursor(QTextCursor.End)
        self.completer.popup().hide()

    def eventFilter(self, obj, event):
        """Process keyboard events"""
        if obj == self:
            cursor = self.textCursor()
            cursor_pos = cursor.position()
            prompt_pos = self.prompt_pos
            if event.type() == QEvent.KeyPress:
                press_key = event.key()
                # only last line can be edited
                if cursor.hasSelection() or cursor_pos < prompt_pos:
                    return True

                # don't allow backspace before prompt
                if press_key == Qt.Key_Backspace and cursor_pos <= prompt_pos:
                    return True

                # enter is pressed
                if press_key == Qt.Key_Return or press_key == Qt.Key_Enter:
                    self.execute_command()
                    return True

                # up arrow is pressed, get history command
                elif press_key == Qt.Key_Up:
                    self.navigate_history(Qt.Key_Up)
                    return True

                # down arrow is pressed, get history command
                elif press_key == Qt.Key_Down:
                    self.navigate_history(Qt.Key_Down)
                    return True

                # swap tab with 4 spaces
                elif press_key == Qt.Key_Tab:
                    cursor.insertText("    ")
                    return True

        return super().eventFilter(obj, event)

    # def insertFromMimeData(self, source):
    #     self.insertPlainText(source.text())
    def _resetbuffer(self):
        """Reset the input buffer."""
        self.buffer = []

    def push(self, line):
        """Push a line to the interpreter"""
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, "<console>")
        if not more:
            self._resetbuffer()
        return more

    def write_output(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)

    def write_prompt(self):
        if self.more:
            self.write_output(self.continue_prompt)
        else:
            self.write_output(self.prompt)
        self.get_prompt_position()

    def get_prompt_position(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        end_pos = cursor.position()
        cursor.movePosition(QTextCursor.StartOfLine)
        self.prompt_pos = cursor.position() + self.prompt_len
        if self.prompt_pos > end_pos:
            self.prompt_pos = end_pos
        return self.prompt_pos

    def get_current_command(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.setPosition(self.prompt_pos, QTextCursor.KeepAnchor)
        full_line = cursor.selectedText()
        return full_line

    def set_current_command(self, cmd):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.setPosition(self.prompt_pos, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(cmd, self.textCursor().charFormat())
        self.moveCursor(QTextCursor.End)

    def navigate_history(self, direction):
        if not self.history:
            return

        # self.history_index is the reverse index of self.history
        if direction == Qt.Key_Up:  # up is pressed
            if abs(self.history_index) >= len(self.history):
                self.history_index = -len(self.history)
            else:
                self.history_index -= 1
        else:  # down is pressed
            self.history_index += 1
            if self.history_index >= 0:
                self.history_index = 0
                self.set_current_command("")
                return

        self.set_current_command(self.history[self.history_index])

    def execute_command(self):
        cmd = self.get_current_command()

        # append cmd to history
        if cmd.strip() and (not self.history or self.history[-1] != cmd):
            self.history.append(cmd)
        self.history_index = 0

        # redirect stdout to output
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.more = self.push(cmd)
        self.write_output("\n")
        result = output.getvalue()
        if result:
            self.write_output(result)
        self.write_prompt()

    def write(self, text):
        """override InteractiveInterpreter.write"""
        self.write_output('\n'+text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interpreter = PythonInterpreter()
    interpreter.setFixedSize(1200, 900)
    interpreter.show()
    sys.exit(app.exec_())
