import random
import time
from rich.console import Console
from rich.table import Table
import os
from rich import print
from rich.layout import Layout
from rich.markdown import Markdown

class Render:

    def table(self,
                CPU_Temperature="N/A",
                CPU_Usage="N/A",
                RAM_Usage="N/A",
                Cipher_Key="N/A",
                Cipher_Text="N/A",
                Decrypted_text="N/A",
                Brocker_IP="N/A",
                Proxy_IP="N/A",
                User="N/A",
                User_ATTRIBUTE="N/A",
                Total_Time="N/A",
                Transmission_Time = "N/A",
                Decrypt_Time = "N/A",
            ):
        os.system('clear')
        # Table 1
        table = Table()
        table.add_column("", justify="right", style="cyan", no_wrap=True)
        table.add_column("Subscriber <- Broker <- Publisher", justify="left", style="green")
        table.add_row("User", User)
        table.add_row("User attribute", User_ATTRIBUTE,end_section=True)
        table.add_row("Remote Device", "Raspberry Pi 3 Model A+", style="gold3")
        table.add_row("CPU Temperature", CPU_Temperature + " °C",style="gold3")
        table.add_row("CPU Usage", CPU_Usage +" %",style="gold3")
        table.add_row("RAM Usage", RAM_Usage +" %",style="gold3")
        table.add_row("Decrypted text", Decrypted_text,style="gold3")
        table.add_row("Cipher AES Key", Cipher_Key,style="gold3")
        table.add_row("Cipher Text", Cipher_Text,style="gold3")
        table.add_row("Brocker IP", Brocker_IP,style="gold3")
        table.add_row("Proxy IP", Proxy_IP,style="gold3")
        table.add_row("Transmission Time", Transmission_Time+" s",style="gold3")
        table.add_row("Decrypt Time", Decrypt_Time+" s",style="gold3")
        table.add_row("Total Time", Total_Time+" s",style="gold3")
        # Table 2
        # table2 = Table()
        # table2.add_column("Cipher AES Key", justify="center", style="cyan", no_wrap=True)
        # table2.add_row(Cipher_Key)
        # layout = Layout()
        # layout.split_column(
        #     Layout(table),
        #     Layout(table2)
        # )
        print(table)

if __name__ == '__main__':
    while True:
        os.system('clear')
        render = Render()
        render.table("50","50","50","AAA")
        time.sleep(2)
    