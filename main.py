import tkinter as tk
from tkinter import ttk, messagebox
from avl_tree import AVLTree
from sorting_algorithms import merge_sort
from tkinter import filedialog
from ttkthemes import ThemedTk
import re

class Contact:
    def __init__(self, first_name, last_name, email, phone):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone

def format_phone_number(phone_number):
  """
  Formata o número de telefone para o padrão (xx) xxxxx-xxxx.
  """
  # Remove caracteres não numéricos
  phone_number = re.sub(r"[^\d]", "", phone_number)

  # Verifica se o número tem 11 dígitos
  if len(phone_number) != 11:
    raise ValueError("Número de telefone inválido. Insira um número com 11 dígitos.")

  # Formata o número
  formatted_number = f"({phone_number[0:2]}) {phone_number[2:7]}-{phone_number[7:]}"

  return formatted_number

def is_valid_email(email):
  """
  Valida se o e-mail está no formato correto.
  """
  regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
  return re.fullmatch(regex, email)

class ContactManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Contatos")

        # Inicializa a lista de contatos e a árvore AVL
        self.contacts = []
        self.contact_tree = AVLTree()

        # Cria a tabela de contatos
        self.tree = ttk.Treeview(root, columns=("Nome", "Sobrenome", "Email", "Telefone"))
        self.tree.heading("#0", text="")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Sobrenome", text="Sobrenome")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Adiciona uma barra de rolagem
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        # Adiciona os widgets à interface
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Inicializa variáveis de seleção
        self.context_menu_visible = False
        self.selected_contact = None
        self.selected_index = None

        # Cria o menu de contexto
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Editar Contato", command=self.edit_selected_contact)
        self.context_menu.add_command(label="Excluir Contato", command=self.delete_selected_contact)

        # Adiciona botões e campos de entrada
        tk.Label(root, text="Nome:").pack()
        self.first_name_entry = tk.Entry(root)
        self.first_name_entry.pack()

        tk.Label(root, text="Sobrenome:").pack()
        self.last_name_entry = tk.Entry(root)
        self.last_name_entry.pack()

        tk.Label(root, text="Email:").pack()
        self.email_entry = tk.Entry(root)
        self.email_entry.pack()

        tk.Label(root, text="Telefone:").pack()
        self.phone_entry = tk.Entry(root)
        self.phone_entry.pack()

        tk.Button(root, text="Adicionar Contato", command=self.add_contact).pack()

        # Inicializa a lista completa de contatos
        self.all_contacts = []

        # Adiciona botão e campo de pesquisa
        tk.Label(root, text="Pesquisar:").pack()
        self.search_entry = tk.Entry(root)
        self.search_entry.pack()

        tk.Button(root, text="Pesquisar", command=self.search_contacts).pack()

        tk.Button(root, text="Limpar", command=self.clear_search).pack()

        # Adiciona um botão para exportar a tabela
        tk.Button(root, text="Exportar Tabela", command=self.export_table).pack()

        # Adiciona um botão para encerrar o programa
        tk.Button(root, text="Encerrar Programa", command=root.destroy).pack()

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.update_table_with_keyword()

    def search_contacts(self):
        keyword = self.search_entry.get().lower()

        if not keyword:
            # Se o campo de pesquisa estiver vazio, exiba todos os contatos
            self.update_table_with_keyword(keyword=None)
        else:
            # Caso contrário, filtre os contatos com base na palavra-chave
            self.update_table_with_keyword(keyword)

    def sort_contacts(self):
        sort_order = self.sort_order_var.get()

        if "Nome" in sort_order:
            key = lambda x: (x.first_name, x.last_name)
        else:
            key = lambda x: x.phone

        reverse_order = "Decrescente" in sort_order

        sorted_contacts = sorted(self.contacts, key=key, reverse=reverse_order)

        # Atualiza a tabela com os contatos ordenados
        self.update_table_with_keyword(keyword=None, contacts=sorted_contacts)

    def add_contact(self):
        new_first_name = self.first_name_entry.get()
        new_last_name = self.last_name_entry.get()
        new_email = self.email_entry.get()
        new_phone = self.phone_entry.get()

        # Verifica se o número de telefone tem 11 dígitos
        if len(new_phone) != 11:
            messagebox.showerror("Número de telefone inválido", "Insira um número com 11 dígitos.")
            return

        # Formata o número de telefone
        new_phone = format_phone_number(new_phone)

        # Valida o endereço de e-mail
        if not is_valid_email(new_email):
            messagebox.showerror(
                "Endereço de e-mail inválido",
                "O endereço de e-mail deve estar no formato nome@exemplo.com.",
            )
            return

        new_contact = Contact(new_first_name, new_last_name, new_email, new_phone)
        if self.is_duplicate(new_contact):
            messagebox.showerror("Erro", "Número ou e-mail já existem. Insira informações únicas.")
            return

        self.contacts.append(new_contact)
        self.all_contacts = self.contacts.copy()

        # Atualiza a árvore AVL
        self.update_avl_tree()

        # Atualiza a tabela
        self.update_table()

        # Atualiza a árvore AVL
        self.contact_tree = self.build_avl_tree_from_contacts(self.all_contacts)

        messagebox.showinfo("Sucesso", "Contato adicionado com sucesso!")
        self.clear_entry_fields()

    def is_duplicate(self, contact):
        """
        Verifica se o contato já existe na lista de contatos.
        """
        for existing_contact in self.contacts:
            if existing_contact.email == contact.email or existing_contact.phone == contact.phone:
                return True
        return False
    def export_table(self):
        # Solicita ao usuário o local para salvar o arquivo
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

        if not file_path:
            # O usuário cancelou a operação
            return

        try:
            # Abre o arquivo para escrita
            with open(file_path, "w") as file:
                # Escreve o cabeçalho formatado
                file.write(f"{self.pad_string('Nome', 20)} {self.pad_string('Sobrenome', 20)} {self.pad_string('Email', 30)} {self.pad_string('Telefone', 15)}\n")
                # Escreve os dados dos contatos formatados
                for contact in self.contacts:
                    file.write(f"{self.pad_string(contact.first_name, 20)} {self.pad_string(contact.last_name, 20)} {self.pad_string(contact.email, 30)} {self.pad_string(contact.phone, 15)}\n")

            messagebox.showinfo("Sucesso", "Tabela exportada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar a tabela: {str(e)}")

    def pad_string(self, string, length):
        # Função para formatar uma string com espaços à direita para atingir o comprimento desejado
        return string.ljust(length)

    def edit_selected_contact(self):
        if self.selected_contact:
            self.edit_info_window = tk.Toplevel(self.root)
            self.edit_info_window.title("Editar Informações")

            tk.Label(self.edit_info_window, text="Nome:").pack()
            self.edit_first_name_entry = tk.Entry(self.edit_info_window)
            self.edit_first_name_entry.insert(0, self.selected_contact.first_name)
            self.edit_first_name_entry.pack()

            tk.Label(self.edit_info_window, text="Sobrenome:").pack()
            self.edit_last_name_entry = tk.Entry(self.edit_info_window)
            self.edit_last_name_entry.insert(0, self.selected_contact.last_name)
            self.edit_last_name_entry.pack()

            tk.Label(self.edit_info_window, text="Email:").pack()
            self.edit_email_entry = tk.Entry(self.edit_info_window)
            self.edit_email_entry.insert(0, self.selected_contact.email)
            self.edit_email_entry.pack()

            tk.Label(self.edit_info_window, text="Telefone:").pack()
            self.edit_phone_entry = tk.Entry(self.edit_info_window)
            self.edit_phone_entry.insert(0, self.selected_contact.phone)
            self.edit_phone_entry.pack()

            tk.Button(self.edit_info_window, text="Aplicar", command=self.apply_edit).pack()
            tk.Button(self.edit_info_window, text="Cancelar", command=self.edit_info_window.destroy).pack()

    def apply_edit(self):
        # Limpar mensagens de erro anteriores
        self.clear_edit_errors()

        new_first_name = self.edit_first_name_entry.get()
        new_last_name = self.edit_last_name_entry.get()
        new_email = self.edit_email_entry.get()
        new_phone = self.edit_phone_entry.get()

        try:
            # Formatar o número de telefone
            if len(new_phone) == 11:
                new_phone = format_phone_number(new_phone)
        except ValueError as e:
            # Lidar com o erro de formatação
            self.show_edit_error(str(e))
            return

        # Validar o endereço de e-mail
        if not is_valid_email(new_email):
            self.show_edit_error("Endereço de e-mail inválido. O e-mail deve estar no formato nome@exemplo.com.")
            return

        # Verificar se alguma informação foi alterada
        if (self.selected_contact.first_name, self.selected_contact.last_name, self.selected_contact.email,
            self.selected_contact.phone) == (new_first_name, new_last_name, new_email, new_phone):
            # Nenhuma alteração feita
            messagebox.showinfo("Sucesso", "Nenhuma alteração feita.")
            self.edit_info_window.destroy()
            return

        # Atualizar o contato selecionado com as novas informações
        self.selected_contact.first_name = new_first_name
        self.selected_contact.last_name = new_last_name
        self.selected_contact.email = new_email
        self.selected_contact.phone = new_phone

        # Reorganizar a árvore AVL
        self.update_avl_tree()

        # Atualizar a tabela
        self.update_table()

        # Exibir mensagem de sucesso
        messagebox.showinfo("Sucesso", "Contato editado com sucesso!")
        self.edit_info_window.destroy()

    def clear_edit_errors(self):
        # Método para limpar mensagens de erro na janela de edição
        for widget in self.edit_info_window.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("fg") == "red":
                widget.destroy()

    def show_edit_error(self, message):
        # Método para exibir mensagens de erro na janela de edição
        error_label = tk.Label(self.edit_info_window, text=message, fg="red")
        error_label.pack()

    def delete_selected_contact(self):
        if self.selected_contact:
            self.contacts.pop(self.selected_index)
            # Atualiza ambas as listas
            self.all_contacts = self.contacts.copy()

            # Atualiza a árvore AVL
            self.update_avl_tree()

            # Atualiza a tabela
            self.update_table()

            self.update_table_with_keyword()
            messagebox.showinfo("Sucesso", "Contato excluído com sucesso!")

    def list_contacts(self, keyword=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if keyword:
            filtered_contacts = [contact for contact in self.contacts if keyword.lower() in contact.first_name.lower() or keyword.lower() in contact.last_name.lower()]
            sorted_contacts = merge_sort(filtered_contacts, key=lambda x: x.phone)
        else:
            sorted_contacts = merge_sort(self.contacts, key=lambda x: x.phone)

        for contact in sorted_contacts:
            self.tree.insert("", "end", values=(contact.first_name, contact.last_name, contact.email, contact.phone))

    def show_context_menu(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Obtém o número de telefone do item selecionado
            selected_phone = self.tree.item(item, "values")[3]

            # Procura o contato com base no número de telefone na lista de contatos
            for i, contact in enumerate(self.contacts):
                if contact.phone == selected_phone:
                    self.selected_index = i
                    self.selected_contact = contact
                    break

            self.context_menu.post(event.x_root, event.y_root)

    def build_avl_tree_from_contacts(self, contacts):
        avl_tree = AVLTree()
        for contact in contacts:
            avl_tree.insert(contact.phone, contact)
        return avl_tree

    def update_avl_tree(self):
        self.contact_tree = self.build_avl_tree_from_contacts(self.all_contacts)

    def update_table(self):
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ordena os contatos
        sorted_contacts = merge_sort(self.contacts, key=lambda x: x.phone)

        # Preenche a tabela com os contatos ordenados
        for contact in sorted_contacts:
            self.tree.insert("", "end", values=(contact.first_name, contact.last_name, contact.email, contact.phone))

    def update_table_with_keyword(self, keyword=None, contacts=None):
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        if contacts is None:
            contacts = self.all_contacts

        # Escolhe a lista a ser exibida com base na palavra-chave
        if keyword:
            # Filtra os contatos que correspondem à palavra-chave
            filtered_contacts = [contact for contact in contacts if
                                 keyword.lower() in contact.first_name.lower() or keyword.lower() in contact.last_name.lower()]
            sorted_contacts = merge_sort(filtered_contacts, key=lambda x: x.phone)
        else:
            # Se não houver palavra-chave, exibe todos os contatos
            sorted_contacts = merge_sort(contacts, key=lambda x: x.phone)

        # Preenche a tabela com os contatos ordenados
        for contact in sorted_contacts:
            self.tree.insert("", "end", values=(contact.first_name, contact.last_name, contact.email, contact.phone))

    def create_search_entry(self):
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack()

    def clear_entry_fields(self):
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)

def main():
    root = ThemedTk(theme="equilux")
    app = ContactManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()