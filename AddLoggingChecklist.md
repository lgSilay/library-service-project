1. Preparation, do this in the file to which you want to add logging:
   ```python
   import logging
   logger = logging.getLogger("logger_name")

WARNING:
Choose the appropriate logging name in ```library_project/settings.py > LOGGINGS > "loggers"```. 
It will most likely have the same name as your app.

2. Then you can add logging using one of this command:
   * ```python        
     logger.debug("Your message", extra={"user": request.user, "data": serializer.data})
   * ```python        
     logger.info("Your message", extra={"user": request.user, "data": serializer.data})
   * ```python        
     logger.warning("Your message", extra={"user": request.user, "data": serializer.data})
   * ```python        
     logger.error("Your message", extra={"user": request.user, "data": serializer.data})

It's a good practice to provide extra information!
