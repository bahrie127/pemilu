from Tkinter import *
from PIL import Image, ImageTk

class App:

	def __init__(self, master):

		frame = Frame(master, width=700, height=900)
		frame.pack()
		frame.pack_propagate(0)

		self.label_img_path = Label(frame, text='Path to the image file')
		self.label_img_path.place(x=10, y=10)

		self.btn_load_img = Button(
			frame, text='Load Image', command=self.load_image)
		self.btn_load_img.place(x=500, y=10)

		image = Image.open('lenna.jpg')
		photo = ImageTk.PhotoImage(image)
		self.label_im = Label(frame, image=photo)
		self.label_im.image = photo # Keep a reference, so it won't get GC'ed
		self.label_im.place(x=10, y=50)

		self.btn_load_model = Button(frame, text='Load Model', command=self.load_model)
		self.btn_load_model.place(x=500, y=110)

		self.label_model_name = Label(frame, text='Model Name')
		self.label_model_name.place(x=500, y=160)

		self.btn_process = Button(frame, text='Process', command=self.process)
		self.btn_process.place(x=500, y=250)

		self.label_prabowo = Label(frame, text='Suara Prabowo')
		self.label_prabowo.place(x=500, y=300)
		
		self.label_jokowi = Label(frame, text='Suara Jokowi')
		self.label_jokowi.place(x=500, y=350)

		self.label_sah = Label(frame, text='Total Suara Sah')
		self.label_sah.place(x=500, y=400)

		self.label_tidaksah = Label(frame, text='Total Tidak Sah')
		self.label_tidaksah.place(x=500, y=450)

		self.prabowo_vote = StringVar(); self.prabowo_vote.set('0')
		self.jokowi_vote = StringVar(); self.jokowi_vote.set('0')
		self.sah_vote = StringVar(); self.sah_vote.set('0')
		self.tidaksah_vote = StringVar(); self.tidaksah_vote.set('0')

		self.label_prabowo_vote = Label(frame, textvariable=self.prabowo_vote)
		self.label_prabowo_vote.place(x=600, y=300)

		self.label_jokowi_vote = Label(frame, textvariable=self.jokowi_vote)
		self.label_jokowi_vote.place(x=600, y=350)

		self.label_sah_vote = Label(frame, textvariable=self.sah_vote)
		self.label_sah_vote.place(x=600, y=400)

		self.label_tidaksah_vote = Label(frame, textvariable=self.tidaksah_vote)
		self.label_tidaksah_vote.place(x=600, y=450)

	def load_image(self):
		return 0

	def load_model(self):
		return 0

	def process(self):
		return 0

root = Tk()
app = App(root)
root.resizable(0,0)
root.mainloop()