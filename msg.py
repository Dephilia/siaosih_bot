#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2022 dephilia <dephilia@MacBook-Pro.local>
#
# Distributed under terms of the MIT license.

"""

"""
import random

def gen_msg():
    wara_imgs = [
        "https://i.imgur.com/3G7rJ06.jpg",
        "https://i.imgur.com/641fRAZ.jpg",
        "https://images.plurk.com/4Wr1If26wnRKEZIllQVIzO.jpg",
        "https://images.plurk.com/2OkhSDoYeOsQGdvb5KM9Pn.jpg",
        "https://images.plurk.com/3czlRTuYeTYqCj5vicDQBq.png",
        "https://images.plurk.com/1M3oSnXNOMVxnOose7Wh8v.jpg",
        "https://images.plurk.com/1NiFD84tWntjhd65rqpofb.png",
        "https://images.plurk.com/3A9xyxub8URuxPUkv83Dnr.jpg",
        "https://images.plurk.com/5d1XD5HZ2AwNzrOtnpQt55.jpg",
        "https://images.plurk.com/tvs6tIDqFOlXQz8ctqyVO.png",
        "https://images.plurk.com/sWJm5E69kECFZXaOuOil5.jpg",
        "https://images.plurk.com/2dyrBaeTXMPaFHZIGM38nc.jpg",
        "https://images.plurk.com/2r7SHhlXE6wevIRTkAShDB.jpg",
        "https://images.plurk.com/37E5uFu1po0gijbDhMXNns.jpg",
        "https://images.plurk.com/2Xe3MqVire3OBI86q9NiTm.jpg",
        "https://images.plurk.com/4OdjjlnhEf0Q6Sl16b0Qpe.jpg",
        "https://images.plurk.com/2DsYS1rTQQpEnHYuIGRrlM.jpg",
        "https://images.plurk.com/63h9OSIKfXU0xMdqUcYbug.gif",
        "https://images.plurk.com/5K7Cfwcvf1KLbuDiNLowfX.gif",
        "https://images.plurk.com/4I499E93XC217BKyyrbfxs.jpg",
        "https://images.plurk.com/45aC4lP3VHMtxbJcmCvn7p.gif",
        "https://images.plurk.com/3D6GtdgKVtdXI85rkpv2gF.jpg",
        "https://images.plurk.com/1boeK01koxCaHKp61bNZE7.jpg",
        "https://images.plurk.com/6fyOZT8o4XRFjRsUYhdDPx.jpg",
        "https://images.plurk.com/7bHAJhlYJLKiRtIdE5cAIg.gif",
        "https://images.plurk.com/7qfy5z0gIhssOS0tXPccLb.jpg",
        "https://images.plurk.com/4CvNeGzN8VuSWDa6fdChCA.gif",
        "https://images.plurk.com/6E7j8fqvN4RqGcMP0W8RD4.gif",
        "https://images.plurk.com/6PEEClMbQe34JVhGDrP56A.jpg",
        "https://images.plurk.com/59YJKOGWSSVK0txkTRm5Ns.jpg",
        "https://images.plurk.com/2KirBTzaFncKxmbWpksyHM.jpg",
        "https://images.plurk.com/K19HiFh8FfJ6ikvkGpNkt.jpg",
        "https://images.plurk.com/6ArFHTvOVCho1ACPV1xWUM.jpg",
        "https://images.plurk.com/7vQkaO6QDEsiCi2pdXYNBu.jpg",
        "https://images.plurk.com/4zXWw4Ox7T4Jy1pipddhwF.jpg",
        "https://images.plurk.com/4wE1pgyKoy6q80CAtqYKcV.jpg",
        "https://images.plurk.com/ViZe8EY8Fov7FTWzaD9rG.jpg",
        "https://images.plurk.com/yHMyyfUQmuHzdCR3XefFC.jpg",
        "https://images.plurk.com/46bzj1vbQOjyqtTVsvhKDj.jpg",
        "https://images.plurk.com/7uBif82MSdV9wlwvEKNd0M.jpg",
        "https://images.plurk.com/3aDEp8slhs78INml84qYmR.gif",
        "https://images.plurk.com/2pHGirk3j8vHCTsfJPvjsE.gif",
        "https://images.plurk.com/47LY6qQBbGjTrQDs1fnWvo.jpg",
        "https://images.plurk.com/5VDnGFc25D5WubtOuuGQLs.gif",
        "https://images.plurk.com/1I9bt5RNjdtf8eKuskSdco.gif",
        "https://images.plurk.com/5p0orzgQw0eZBSrrnfVvk8.jpg",
        "https://images.plurk.com/1LBwMqxj15mNDrInv9x09f.jpg",
        "https://images.plurk.com/44ift3DX1eKGITeU1gxzKo.jpg",
        "https://images.plurk.com/1WjLQvgqaEhEptA3GOLtxe.png",
        "https://images.plurk.com/4NI5j9G032Ej94pKz2DVdr.gif",
        "https://images.plurk.com/1fMhrVMAcEheOe8aKYUPMG.jpg",
        "https://images.plurk.com/6i9p8fq1IOPaASKwFlLBEw.jpg",
        "https://images.plurk.com/N9ny55giShpK052P7TU8U.jpg",
        "https://images.plurk.com/1SR9y2XF4N5BJv19sBsh4c.jpg",
        "https://images.plurk.com/274nBeksho0DwJO7Py1dAX.png",
        "https://images.plurk.com/qlzv3DXyXbdc6VcA8Zhpa.gif",
        "https://images.plurk.com/3fIHpkJX0Wfxob2afGzldg.jpg",
        "https://images.plurk.com/6j82CzcV84CNDFr11nk33o.gif",
        "https://images.plurk.com/34UeK1zvIMXufXCcWBZIme.gif",
        "https://images.plurk.com/2yVZq4IqvV4mNkKUNKR3MT.jpg",
        "https://images.plurk.com/6huuRnQ823CP75Zh35GfiN.gif",
        "https://images.plurk.com/QYkMFAmkjnIO5of5xjZRk.jpg",
        "https://images.plurk.com/3mSpHWBu550r2rdKl0wk0c.gif",
        "https://images.plurk.com/5FXj7gQ3SaVhd7xbIG4sP7.gif"
    ]
    rand_num = random.randint(1, 100)

    if rand_num <= 3:
        return '草'
    elif rand_num <= 10:
        return random.choice(wara_imgs) + ' \n笑死'
    elif rand_num <= 20:
        return '哭啊'
    else:
        return '笑死'
