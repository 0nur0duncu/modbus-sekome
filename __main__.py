import os, time, asyncio, subprocess, struct
import pymodbus.client as modbusClient
# from pymodbus.exceptions import ConnectionException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import subprocess
from config import Config
import requests

mevcut_dizin = os.getcwd()
error_log_path = os.path.join(mevcut_dizin, "error.log")

is_connected_secome = True
linkManager = True
client = None

async def red_flag_fixer():
    global client
    global linkManager
    if(linkManager==False):
        subprocess.Popen("C:\\PROGRA~1\\Secomea\\LinkManager\\LinkManagerTray.exe")
        linkManager = True
    if(linkManager == True):   
        option= webdriver.ChromeOptions()
        #driver = webdriver.Chrome()
        driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager().install()),options=option)
        #driver = webdriver.Chrome(service=webdriver.ChromeService(ChromeDriverManager(version="114.0.5735.90").install()),options=option)

        url = "https://gm04.secomea.com/lm"
        driver.get(url)
        driver.maximize_window()                

        wait = WebDriverWait(driver, 10)

        modeCert1 = wait.until(EC.element_to_be_clickable((By.ID, "r_cert")))
        modeCert1.click()
        time.sleep(1)

        file_path = os.path.join(os.getcwd(), '<-->.lmc')

        file_input = wait.until(EC.element_to_be_clickable((By.ID, "certfile")))

        file_input.send_keys(file_path)

        password = wait.until(EC.element_to_be_clickable((By.NAME, "pass")))
        password.send_keys("<KEY>")

        login = wait.until(EC.element_to_be_clickable((By.NAME, "login")))
        login.click()
        
        time.sleep(0.5)
        
        nom1 =  wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[1]/button")))
        nom1.click()
        
        time.sleep(0.5)
        
        accountButton = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/ul/li[4]")))
        accountButton.click()
        
        time.sleep(0.5)
        
        keepButton = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div/div/div[1]/div[1]/form/table/tbody/tr[11]/td[2]/input")))
        keepButton.click()
        
        time.sleep(0.5)
        
        saveButton = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div/div/div[1]/div[1]/form/input[1]")))
        saveButton.click()
        
        time.sleep(0.5)
        
        mainButton = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/ul/li[1]")))
        mainButton.click()
        
        time.sleep(0.5)

        nom2 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div[1]/div[3]/ul/li/ul/li/a")))
        nom2.click()
        
        nom3 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div[1]/div[3]/ul/li/ul/li/ul/li[8]")))
        nom3.click()
        
        time.sleep(5)
        connectButtonControl = driver.find_element(By.XPATH,"/html/body/div[4]/div/div[2]/div[2]/div[1]/button[1]").is_displayed()
        connectButtonClickControl = "Connect" in driver.find_element(By.XPATH,"/html/body/div[4]/div/div[2]/div[2]/div[1]/button[1]").get_attribute("outerHTML")
        time.sleep(2)
        if(connectButtonControl == True & connectButtonClickControl == True) :
            nom4 = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div[2]/div[2]/div[1]/button[1]")))
            nom4.click()
        elif(connectButtonControl == False):
            buttonControl(connectButtonControl,driver,linkManager)
        time.sleep(10)
        driver.close()           
      
async def buttonControl(connectButtonControl,driver):
      while connectButtonControl == False:
        try:
            driver.close()
            time.sleep(2)
            connect_to_modbus(client)
        except Exception as ex:
            with open(error_log_path, "a") as dosya:
                dosya.write(str(ex))

async def initialize_client():
    client = modbusClient.AsyncModbusTcpClient(
        host=Config.MODBUS_IP.value,
        port=Config.MODBUS_PORT.value
    )
    await client.connect()
    return client

async def connect_to_modbus(client):
    try:
        await client.connect()
        return client
    except Exception as ex:
        with open(error_log_path, "a") as dosya:
            dosya.write(str(ex))
        await red_flag_fixer()
        return False 
    
async def close_from_modbus(client):
    try:
        await client.close()
        return client
    except Exception as e:
        return False          

def convert_to_single(registers):
    value = registers[1]
    value2 = registers[0]
    
    bytes_value = bytearray(struct.pack('<i', value))
    bytes_value2 = bytearray(struct.pack('<i', value2))
    
    value3 = bytes_value2[0:2] + bytes_value[0:2]
    
    return struct.unpack('<f', value3)[0]

async def convert_register_to_float(port):
    raw_value = await client.read_holding_registers(port, count=2)
    number = convert_to_single(raw_value.registers)
    return number

async def  convert_register_to_int(port):
    raw_value = await client.read_holding_registers(port, count=2)
    return raw_value.registers[0]


async def executor_fun():
    global client
    global is_connected_secome   
    while True:
        if ((client != False) and (client is not None) and (client.connected == True) and (is_connected_secome == True)):
            try:

                makine_hiz = round(await convert_register_to_float(Config.MAKINE_HIZI.value), 2)

                lamine_gerginlik_kg = round(await convert_register_to_float(Config.LAMINE_GERGINLIK_KG.value), 2)

                laminasyon_silindir_isisi_celcius = round(await convert_register_to_float(Config.LAMINASYON_SILINDIR_ISI_CELC.value), 2)
                laminasyon_tekne_isisi_celcius = round(await convert_register_to_float(Config.LAMINASYON_TEKNE_ISI_CELC.value), 2)
                laminasyon_sag_siyirici_isisi_celcius = round(await convert_register_to_float(Config.LAMINASYON_SAG_SIYIRICI_ISI_CELC.value), 2)
                laminasyon_sol_siyirici_isisi_celcius = round(await convert_register_to_float(Config.LAMINASYON_SOL_SIYIRICI_ISI_CELC.value), 2)

                kumas_ayirma_buton = round(await convert_register_to_float(Config.KUMAS_AYIRMA_BUTON.value), 2)

                kaymaz_1_silindir_isisi_celcius = round(await convert_register_to_float(Config.KAYMAZ_1_SILINDIR_ISI_CELC.value), 2)
                kaymaz_1_tekne_isisi_celcius = round(await convert_register_to_float(Config.KAYMAZ_1_TEKNE_ISI_CELC.value), 2)
                kaymaz_1_sag_siyirici_isisi_celcius  = round(await convert_register_to_float(Config.KAYMAZ_1_SAG_SIYIRICI_ISI_CELC.value), 2)
                kaymaz_1_sol_siyirici_isisi_celcius  = round(await convert_register_to_float(Config.KAYMAZ_1_SOL_SIYIRICI_ISI_CELC.value), 2)

                kaymaz_2_silindir_isisi_celcius = round(await convert_register_to_float(Config.KAYMAZ_2_SILINDIR_ISI_CELC.value), 2)
                kaymaz_2_tekne_isisi_celcius = round(await convert_register_to_float(Config.KAYMAZ_2_TEKNE_ISI_CELC.value), 2)
                kaymaz_2_sag_siyirici_isisi_celcius  = round(await convert_register_to_float(Config.KAYMAZ_2_SAG_SIYIRICI_ISI_CELC.value), 2)
                kaymaz_2_sol_siyirici_isisi_celcius  = round(await convert_register_to_float(Config.KAYMAZ_2_SOL_SIYIRICI_ISI_CELC.value), 2)

                payload = {
                    "makine_hiz": makine_hiz,
                    "lamine_gerginlik": lamine_gerginlik_kg,
                    "laminasyon_silindir_isi": laminasyon_silindir_isisi_celcius,
                    "laminasyon_tekne_isi": laminasyon_tekne_isisi_celcius,
                    "laminasyon_sag_siyirici_isi": laminasyon_sag_siyirici_isisi_celcius,
                    "laminasyon_sol_siyirici_isi": laminasyon_sol_siyirici_isisi_celcius,
                    "kumas_ayirma_buton": kumas_ayirma_buton,  # Eğer boolean ise True/False kullanabilirsin
                    "kaymaz_1_silindir_isi": kaymaz_1_silindir_isisi_celcius,
                    "kaymaz_1_tekne_isi": kaymaz_1_tekne_isisi_celcius,
                    "kaymaz_1_sag_siyirici_isi": kaymaz_1_sag_siyirici_isisi_celcius,
                    "kaymaz_1_sol_siyirici_isi": kaymaz_1_sol_siyirici_isisi_celcius,
                    "kaymaz_2_silindir_isi": kaymaz_2_silindir_isisi_celcius,
                    "kaymaz_2_tekne_isi": kaymaz_2_tekne_isisi_celcius,
                    "kaymaz_2_sag_siyirici_isi": kaymaz_2_sag_siyirici_isisi_celcius,
                    "kaymaz_2_sol_siyirici_isi": kaymaz_2_sol_siyirici_isisi_celcius
                }

                response = requests.post(Config.SUNUCU_URL.value, json=payload)
                if response.status_code == 200:
                    time.sleep(Config.WAIT_TIME.value)
                else:
                    with open(error_log_path, "a") as dosya:
                        dosya.write("Veriler sunucuya gönderilemedi.")

            except Exception as e:
                with open(error_log_path, "a") as dosya:
                    dosya.write(str(e))
                continue
        else:
            try:
                client = await initialize_client()
            except Exception as e:
                with open(error_log_path, "a") as dosya:
                    dosya.write(str(e))
                await asyncio.sleep(5)  # Wait before retrying

async def main():
    global client
    try:
        client = await initialize_client()
        await executor_fun()
    except Exception as e:
        with open(error_log_path, "a") as dosya:
            dosya.write(str(e))

if __name__ == "__main__":
    asyncio.run(main())
