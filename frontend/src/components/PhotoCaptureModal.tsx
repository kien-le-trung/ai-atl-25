import { useState, useRef } from "react";
import { Camera, Upload, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface PhotoCaptureModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onPhotoCapture: (file: File, name: string, location: string) => void;
}

export function PhotoCaptureModal({ open, onOpenChange, onPhotoCapture }: PhotoCaptureModalProps) {
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleSubmit = () => {
    if (file) {
      onPhotoCapture(file, name, location);
      handleClose();
    }
  };

  const handleClose = () => {
    setPreview(null);
    setFile(null);
    setName("");
    setLocation("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md" data-testid="dialog-photo-capture">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">Capture Photo</DialogTitle>
          <DialogDescription>
            Take or upload a photo to identify the person and start a conversation
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {preview ? (
            <div className="space-y-4">
              <div className="relative">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full h-64 object-cover rounded-md"
                  data-testid="img-preview"
                />
                <Button
                  size="icon"
                  variant="ghost"
                  className="absolute top-2 right-2"
                  onClick={() => {
                    setPreview(null);
                    setFile(null);
                  }}
                  data-testid="button-clear-photo"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label htmlFor="name">Person Name (Optional)</Label>
                  <Input
                    id="name"
                    placeholder="Enter name if new contact"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    data-testid="input-name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location">Location (Optional)</Label>
                  <Input
                    id="location"
                    placeholder="Where did you meet?"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    data-testid="input-location"
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
                data-testid="input-file"
              />
              <Button
                variant="outline"
                className="w-full h-32 border-2 border-dashed hover-elevate active-elevate-2"
                onClick={() => fileInputRef.current?.click()}
                data-testid="button-upload"
              >
                <div className="flex flex-col items-center gap-2">
                  <Upload className="w-8 h-8" />
                  <span className="text-sm font-medium">Upload Photo</span>
                </div>
              </Button>
            </div>
          )}

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={handleClose} data-testid="button-cancel">
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!file}
              data-testid="button-submit"
            >
              <Camera className="w-4 h-4 mr-2" />
              Continue
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
